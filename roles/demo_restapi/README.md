# Ansible Integration Example - Building a Role

TODO: Talk about using filter plugins as another trick to add a small python function but not have to commit to building an entire python module.
TODO: Talk about using `module_defaults`
TODO: Add reference to https://www.redhat.com/sysadmin/ansible-web-endpoints
TODO: Look at https://karneliuk.com/2019/08/rest-api-2-basics-cheat-sheet-ansible-bash-postman-and-python-for-post-delete-using-netbox-and-docker-as-examples/
TODO: Provide examples using https://httpbin.org/ to show REST API functionality

## Overview

Example of using Ansible's [uri](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/uri_module.html) module to integrate with external systems using web service APIs. In this example the external system uses a REST API, however it can be [SOAP, XML-RPC, or JSON-RPC](https://rapidapi.com/blog/types-of-apis/).

We tend to build Ansible python modules to support and integrate with systems/endpoints that currently do not have any existing Ansible modules. However, it's my belief that doing so can add a lot of technical debt and training and maintenance to the team managing the custom python modules. Ansible offers an alternative that keeps you in the Ansible world (not doing lower level python code). Using the `uri` module and some other tricks and good Ansible practices gives you an Ansible Role that is not only idempotent, but provides a wrapper for the endpoint.

This role has been implemented to demostrate the following:

- You don't need python
- Integration with systems using REST API or XML, etc
- Task files are built as API wrappers
- Task files are themselves idempotent
- System agnostic API (windows, linux, etc)
- Environment/platform agnostic (reference dev/test/prod endpoints easily)
- Variables loaded based on OS family (dynamically)
- Task files as APIs (having inputs and outputs)
- Optionally add Ansible filter plugins to support advanced operations (see explanation below)
- Uses Ansible's `module_defaults` to simplify code (eliminate repetitive code)

## Endpoint

This example provides functionality to add server and accounts to CA PAM for Linux and Windows operating systems.

## Support

Some basic things to understand:

- The automation code handles adding the device and related target application and accounts to CA PAM.
- It has been scaled down to solely handle the `root` user for Linux machines and the `hcladmin` and `mistadmin` for Windows machines.
- It does not do anything with the `Administrator` account on Windows machines, because this is not used by CA PAM
- The code is idempotent and can be executed against a device that is already added to CA PAM.
- It is strongly suggested to use the `capam_force=true` extra variable to make the code first delete any existing entry in CA PAM before attempting to add the device. The reason being, the entry may have been added incorrectly or is a result of "corrupt/old" data, or may have been partially added due to an error.

In some cases, a device is built for a specific application - such as Tomcat, Apache, MS SQL, etc. In these cases, the base device will be added to CA PAM, however you will need to alert the CA PAM team to add any other "special" accounts. This approach was agreed with the HCL Automation Team *and* the CA PAM team since CA PAM is going to be replaced by CyberArk and the goal of this automation code is to "simplify" and help the CA PAM with the basic operation of adding a device to CA PAM - which is an operation that happens often.

## Variables

Variables from the `ansible-playbooks` repo override default values in the `defaults/main.yml`.

- `hosts/000_shared_vars.yml` holds the username/password/server to connect to CA PAM via REST API
- `hosts/azure/lab/group_vars/all/lab.yml` holds Azure overriding variables to connect to CA PAM development server 
- `hosts/htc/lab/group_vars/all/lab.yml` holds HTC overriding variables to connect to CA PAM development server
- `hosts/htc/100_htc_vars.yml` - holds account passwords for root, hcladmin and mistadmin specific to HTC servers
- `hosts/azure/100_azure_vars.yml` - holds account passwords for root, hcladmin and mistadmin specific to Azure servers
- `hosts/azure/{dev,test,prod,lab}/group_vars/all/{dev,test,prod,lab}.yml` - contains special variables that define device group IDs (capam_windows_device_groups) and server location (capam_server_location)

## Usage

The following information should help you understand how to use this role.

- add a device, using brute force method
    ```
    ansible-playbook -i inventory capam_server_add.yml -e hostname=linux.example.com -e capam_force=true
    ```

- delete a device
    ```
    ansible-playbook -i inventory capam_server_delete.yml -e hostname=linux.example.com
    ```

Deleting a device from CA PAM does not require being able to connect to the server. The server is removed directly from CA PAM. This can be useful in cases when you need to cleanup data in CA PAM that might be referring to a server that no longer exists (cannot connect to the machine).

Supporting API:

- `server_add.yml`: Add server to CA PAM (platform agnostic)
- `server_delete.yml`: Delete a server/device from CA PAM (platform agnostic)
- `export_data.yml`: Export data within CA PAM to local JSON file (used only for development and debug purposes)

## Testing

To test the role and run the unit tests, use the following command format:

```
cd tests
ansible-playbook -i inventory test.yml
```

## Rest API

This role uses REST API to connect to CA PAM to perform operations. For testing purposes you can view what is stored in CA PAM by using the following URLs in your browser to see info about a specific device. You will be asked for login information when you first attempt one of these URLs - simply enter the credentials.

Get list of devices added to CA PAM:
```
https://capam.example.com/api.php/v1/devices.json
```

Search for device settings in CA PAM (provide the FQDN):
```
https://capam.example.com/api.php/v1/devices.json?deviceName=server.example.com
```

Get device details using deviceId:
```
https://capam.example.com/api.php/v1/devices.json/{deviceId}/
```

Get password view policies:
```
https://capam.example.com/api.php/v1/passwords/viewPolicies.json
```

Get password composition policies:
```
https://capam.example.com/api.php/v1/passwords/compositionPolicies.json
```

Get device access methods (you need to know the deviceId value):
```
https://capam.example.com/api.php/v1/devices.json/{deviceId}/accessMethods
```

Get services information:
```
https://capam.example.com/api.php/v1/services.json
```

Get policies:
```
https://capam.example.com/api.php/v1/policies.json
```

Get user groups:
```
https://capam.example.com/api.php/v1/userGroups.json
```

Get device groups:
```
https://capam.example.com/api.php/v1/deviceGroups.json
```

For more REST API documentation with CA PAM, you might want to take a look at the following websites:

* [CA PAM documentation - messages](https://techdocs.broadcom.com/content/broadcom/techdocs/us/en/ca-enterprise-software/layer7-privileged-access-management/privileged-access-manager/3-1-1/reference/messages-and-log-formats.html)
* [CA PAM documentation - rest api](https://techdocs.broadcom.com/content/broadcom/techdocs/us/en/ca-enterprise-software/layer7-privileged-access-management/privileged-access-manager/3-1-1/programming/external-api-for-integrating-applications/use-the-external-api-programmers.html#toccontentbroadcomtechdocsusencaenterprisesoftwarelayer7privilegedaccessmanagementprivilegedaccessmanager311referencehtmlReference)
* [CA PAM documentation - rest api error messages](https://techdocs.broadcom.com/content/broadcom/techdocs/us/en/ca-enterprise-software/layer7-privileged-access-management/privileged-access-manager/3-1-3/reference/messages-and-log-formats/pam-cmn-common-messages.html)
