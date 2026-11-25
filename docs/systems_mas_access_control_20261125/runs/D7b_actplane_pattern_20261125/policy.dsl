source AGENT = exec "**/python*"
rule protect:
  block write file "*forbidden" if AGENT
  because "D7b suffix pattern for preopened FD"
