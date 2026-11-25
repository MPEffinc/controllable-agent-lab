source AGENT = exec "**/python*"
rule protect:
  block write file "/work/service.sqlite" if AGENT
  because "B4 agent cannot directly write database"
