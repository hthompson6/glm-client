# Licensing
Scripts associated with licensing A10 products.

The GLM_API_calls.py contains methods to activate to vThunder, revoke a license or revoke an activation. Each method contains an example of usage.


'''
Example configuration to register a vThunder with a Flexpool (subscription license)(ACOS v4.1.4-P1.69)

vThunder-Active-affinity-def-vMaster[4/1](config:2)#show run glm
!Section configuration: 94 bytes
!
glm use-mgmt-port
glm enable-requests
glm allocate-bandwidth 200
glm token vThd10516000
!
Run this command to update changes to GLM:

  glm send license-request
'''
