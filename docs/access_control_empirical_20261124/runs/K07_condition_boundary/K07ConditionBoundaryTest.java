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
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** Independent boundary test; it does not run the NGAC-IR generator. */
public class K07ConditionBoundaryTest {

    private enum Mode { BROAD, STRICT, APP_PM }

    @Test
    void conditionalReadBoundary() throws PMException {
        for (Mode mode : Mode.values()) {
            for (boolean registrationOpen : new boolean[] {false, true}) {
                runOne(mode, registrationOpen);
            }
        }
    }

    private void runOne(Mode mode, boolean registrationOpen) throws PMException {
        MemoryPAP pap = new MemoryPAP();
        AtomicInteger effects = new AtomicInteger();
        pap.modify().operations().setResourceAccessRights(new AccessRightSet("read"));

        long pc = pap.modify().graph().createPolicyClass("pc");
        long ua = pap.modify().graph().createUserAttribute("members", List.of(pc));
        long user = pap.modify().graph().createUser("alice", List.of(ua));
        long oa = pap.modify().graph().createObjectAttribute("docs", List.of(pc));
        long doc = pap.modify().graph().createObject("doc", List.of(oa));

        if (mode != Mode.STRICT) {
            pap.modify().graph().associate(ua, oa, new AccessRightSet("read"));
        }

        NodeNameFormalParameter name = new NodeNameFormalParameter("name");
        pap.modify().operations().createOperation(new ResourceOperation<Void>(
            "read_doc",
            VOID_TYPE,
            List.of(name),
            List.of(new RequiredCapability(
                new RequiredPrivilegeOnParameter(name, new AccessRightSet("read"))
            ))
        ) {
            @Override
            public Void execute(PolicyQuery query, Args args) {
                effects.incrementAndGet();
                return null;
            }
        });

        IdUserContext userCtx = new IdUserContext(user);
        boolean pmAllow = pap.query().access()
            .computePrivileges(userCtx, new IdTargetContext(doc)).contains("read");
        int before = effects.get();
        boolean appAllow = mode != Mode.APP_PM || registrationOpen;
        boolean pdpInvoked = appAllow;
        String finalDecision;
        if (!appAllow) {
            finalDecision = "DENY_APP";
        } else {
            try {
                new PDP(pap).adjudicateOperation(userCtx, "read_doc", Map.of("name", "doc"));
                finalDecision = "ALLOW";
            } catch (UnauthorizedException denied) {
                finalDecision = "DENY_PM";
            }
        }
        int after = effects.get();

        boolean exportedAssociation = mode != Mode.STRICT;
        int expectedAfter = switch (mode) {
            case BROAD -> 1;
            case STRICT -> 0;
            case APP_PM -> registrationOpen ? 1 : 0;
        };
        assertEquals(exportedAssociation, pmAllow, "PM privilege for " + mode);
        assertEquals(expectedAfter, after, "Actual effect for " + mode + "/" + registrationOpen);
        assertEquals(0, before, "Fresh in-memory effect ledger per case");

        System.out.printf(
            "K07_RAW {\"mode\":\"%s\",\"registration_open\":%s,"
                + "\"association_exported\":%s,\"pm_allow\":%s,"
                + "\"app_allow\":%s,\"pdp_invoked\":%s,"
                + "\"final_decision\":\"%s\",\"effect_before\":%d,\"effect_after\":%d}%n",
            mode, registrationOpen, exportedAssociation, pmAllow,
            appAllow, pdpInvoked, finalDecision, before, after
        );
    }
}
