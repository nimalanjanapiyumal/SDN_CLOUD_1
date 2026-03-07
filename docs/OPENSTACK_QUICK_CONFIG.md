# OpenStack quick configuration for the dashboard

The dashboard uses `openstacksdk`. To avoid the `auth_url` error, configure one of the following.

## Option A: clouds.yaml

Copy `docs/clouds.yaml.example` to `~/.config/openstack/clouds.yaml` and update the values.

```yaml
clouds:
  mycloud:
    auth_type: password
    auth:
      auth_url: http://OPENSTACK_CONTROLLER:5000/v3
      username: demo
      password: secret
      project_name: demo
      user_domain_name: Default
      project_domain_name: Default
    region_name: RegionOne
    interface: public
    identity_api_version: 3
```

Then run:

```bash
export OS_CLOUD=mycloud
bash manage.sh dashboard start
```

## Option B: environment variables

```bash
export OS_AUTH_TYPE=password
export OS_AUTH_URL=http://OPENSTACK_CONTROLLER:5000/v3
export OS_USERNAME=demo
export OS_PASSWORD=secret
export OS_PROJECT_NAME=demo
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
bash manage.sh dashboard start
```

If you do not want OpenStack visibility on this VM, disable it:

```bash
export OPENSTACK_ENABLED=false
bash manage.sh dashboard start
```
