import re

# s = ' IVY-1616 Properly parse the artifact origin location, if the location is a file: URI'
# pat = re.compile(r'IVY-\d+')
# res = pat.findall(s)
# print(res[0].split('IVY-')[1])


s = 'maven-repository-discovery/src/main/java/org/apache/maven/repository/discovery/AbstractArtifactDiscoverer.java'
print(len(s.split()))