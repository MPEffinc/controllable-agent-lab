source AGENT = exec "**/python*"
rule protect:
  block write file "/work/forbidden" if AGENT
  because "D7 forbidden path after attach"
