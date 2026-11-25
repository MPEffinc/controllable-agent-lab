source AGENT = exec "**/python*"
rule protect:
  block write file "forbidden" if AGENT
  because "D7c basename rule for preopened FD"
