source AGENT = exec "**/bash"
rule protect:
  block write file "/work/forbidden" if AGENT
  because "D5 forbidden path"
