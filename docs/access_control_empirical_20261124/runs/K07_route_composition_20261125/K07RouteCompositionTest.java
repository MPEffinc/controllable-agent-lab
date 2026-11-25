package gov.nist.csd.pm.core.example;

import static gov.nist.csd.pm.core.pap.operation.arg.type.BasicTypes.VOID_TYPE;
import static org.junit.jupiter.api.Assertions.assertEquals;

import gov.nist.csd.pm.core.common.exception.PMException;
import gov.nist.csd.pm.core.impl.memory.pap.MemoryPAP;
import gov.nist.csd.pm.core.pap.operation.ResourceOperation;
import gov.nist.csd.pm.core.pap.operation.accessright.AccessRightSet;
import gov.nist.csd.pm.core.pap.operation.arg.Args;
import gov.nist.csd.pm.core.pap.operation.param.NodeNameFormalParameter;
import gov.nist.csd.pm.core.pap.operation.reqcap.RequiredCapability;
import gov.nist.csd.pm.core.pap.operation.reqcap.RequiredPrivilegeOnParameter;
import gov.nist.csd.pm.core.pap.query.PolicyQuery;
import gov.nist.csd.pm.core.pap.query.model.context.IdTargetContext;
import gov.nist.csd.pm.core.pap.query.model.context.IdUserContext;
import gov.nist.csd.pm.core.pdp.PDP;
import gov.nist.csd.pm.core.pdp.UnauthorizedException;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** Independent composition counterexample, not the NGAC-IR authors' implementation. */
public class K07RouteCompositionTest {

    private record Scenario(String name, boolean alternate, boolean registrationOpen,
                            boolean conditionalProhibitionRule, boolean embargoActive,
                            boolean exportProhibition) {}

    private static final List<Scenario> SCENARIOS = List.of(
        new Scenario("conditional_only_closed", false, false, false, false, false),
        new Scenario("conditional_only_open", false, true, false, false, false),
        new Scenario("alternate_closed", true, false, false, false, false),
        new Scenario("alternate_open", true, true, false, false, false),
        new Scenario("embargo_inactive_always_export", true, false, true, false, true),
        new Scenario("embargo_active_always_export", true, false, true, true, true),
        new Scenario("embargo_inactive_aware_export", true, false, true, false, false)
    );

    @Test
    void routeComposition() throws PMException {
        for (Scenario s : SCENARIOS) {
            runOne(s);
        }
    }

    private static void runOne(Scenario s) throws PMException {
        MemoryPAP pap = new MemoryPAP();
        AtomicInteger naiveEffects = new AtomicInteger();
        AtomicInteger routeEffects = new AtomicInteger();
        pap.modify().operations().setResourceAccessRights(new AccessRightSet("read"));

        long pc = pap.modify().graph().createPolicyClass("pc");
        long conditionalUa = pap.modify().graph().createUserAttribute("conditional", List.of(pc));
        long alternateUa = pap.modify().graph().createUserAttribute("alternate", List.of(pc));
        long user = pap.modify().graph().createUser("alice", List.of(conditionalUa, alternateUa));
        long oa = pap.modify().graph().createObjectAttribute("docs", List.of(pc));
        long doc = pap.modify().graph().createObject("doc", List.of(oa));

        // This broad association deliberately loses the first route's condition.
        pap.modify().graph().associate(conditionalUa, oa, new AccessRightSet("read"));
        if (s.alternate) {
            pap.modify().graph().associate(alternateUa, oa, new AccessRightSet("read"));
        }
        if (s.exportProhibition) {
            pap.modify().prohibitions().createNodeProhibition(
                "deny_read", user, new AccessRightSet("read"), Set.of(oa), Set.of(), true);
        }

        addOperation(pap, "read_naive", naiveEffects);
        addOperation(pap, "read_route", routeEffects);
        IdUserContext userCtx = new IdUserContext(user);
        boolean pmAllow = pap.query().access()
            .computePrivileges(userCtx, new IdTargetContext(doc)).contains("read");

        boolean naiveGate = s.registrationOpen;
        boolean routeGate = s.registrationOpen || s.alternate;
        String naiveDecision = invokeIfAllowed(pap, userCtx, "read_naive", naiveGate);
        String routeDecision = invokeIfAllowed(pap, userCtx, "read_route", routeGate);
        boolean intended = (s.registrationOpen || s.alternate)
            && !(s.conditionalProhibitionRule && s.embargoActive);

        assertEquals(!s.exportProhibition, pmAllow, "PM decision: " + s.name);
        assertEquals(naiveGate && pmAllow ? 1 : 0, naiveEffects.get(), "Naive effect: " + s.name);
        assertEquals(routeGate && pmAllow ? 1 : 0, routeEffects.get(), "Route effect: " + s.name);

        System.out.printf(
            "K07_ROUTE_RAW {\"case\":\"%s\",\"alternate\":%s,\"registration_open\":%s,"
                + "\"conditional_prohibition_rule\":%s,\"embargo_active\":%s,"
                + "\"export_prohibition\":%s,\"pm_allow\":%s,\"intended_allow\":%s,"
                + "\"naive_gate\":%s,\"naive_pdp_invoked\":%s,\"naive_decision\":\"%s\","
                + "\"naive_effect_before\":0,\"naive_effect_after\":%d,"
                + "\"route_gate\":%s,\"route_pdp_invoked\":%s,\"route_decision\":\"%s\","
                + "\"route_effect_before\":0,\"route_effect_after\":%d}%n",
            s.name, s.alternate, s.registrationOpen, s.conditionalProhibitionRule,
            s.embargoActive, s.exportProhibition, pmAllow, intended,
            naiveGate, naiveGate, naiveDecision, naiveEffects.get(),
            routeGate, routeGate, routeDecision, routeEffects.get()
        );
    }

    private static void addOperation(MemoryPAP pap, String name, AtomicInteger effects) throws PMException {
        NodeNameFormalParameter param = new NodeNameFormalParameter("name");
        pap.modify().operations().createOperation(new ResourceOperation<Void>(
            name, VOID_TYPE, List.of(param),
            List.of(new RequiredCapability(
                new RequiredPrivilegeOnParameter(param, new AccessRightSet("read"))
            ))
        ) {
            @Override
            public Void execute(PolicyQuery query, Args args) {
                effects.incrementAndGet();
                return null;
            }
        });
    }

    private static String invokeIfAllowed(MemoryPAP pap, IdUserContext userCtx,
                                          String operation, boolean appGate) throws PMException {
        if (!appGate) {
            return "DENY_APP";
        }
        try {
            new PDP(pap).adjudicateOperation(userCtx, operation, Map.of("name", "doc"));
            return "ALLOW";
        } catch (UnauthorizedException denied) {
            return "DENY_PM";
        }
    }
}
