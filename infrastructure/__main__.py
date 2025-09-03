import pulumi
import pulumi_azure_native as azure

# Load Pulumi stack config
config = pulumi.Config()
location = config.get("azure:location") or "eastus"
env = config.get("azure:env") or "dev"

prefix = f"qa-{env}"

# Resource Group
rg = azure.resources.ResourceGroup(f"{prefix}-rg",
    resource_group_name=f"{prefix}-rg",
    location=location
)

# Container Group (empty image placeholder for now)
container_group = azure.containerinstance.ContainerGroup(f"{prefix}-aci",
    resource_group_name=rg.name,
    location=rg.location,
    os_type="Linux",
    containers=[azure.containerinstance.ContainerArgs(
        name=f"{prefix}-app",
        image="mcr.microsoft.com/azuredocs/aci-helloworld",  # temporary placeholder
        resources=azure.containerinstance.ResourceRequirementsArgs(
            requests=azure.containerinstance.ResourceRequestsArgs(
                cpu=1.0,
                memory_in_gb=1.5
            )
        ),
        ports=[azure.containerinstance.ContainerPortArgs(port=80)]
    )],
    ip_address=azure.containerinstance.IpAddressArgs(
        ports=[azure.containerinstance.PortArgs(port=80, protocol="TCP")],
        type="Public"
    )
)

# Export outputs
pulumi.export("app_fqdn", container_group.ip_address.apply(lambda ip: ip.fqdn))
pulumi.export("container_group_name", container_group.name)
pulumi.export("resource_group_name", rg.name)
