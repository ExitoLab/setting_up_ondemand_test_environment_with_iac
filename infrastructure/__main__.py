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

# Docker image passed from config (e.g. Pulumi.dev.yaml)
docker_image = config.get("docker:image") or "mcr.microsoft.com/azuredocs/aci-helloworld"

# Container Group
container_group = azure.containerinstance.ContainerGroup(f"{prefix}-aci",
    resource_group_name=rg.name,
    location=rg.location,
    os_type="Linux",
    containers=[azure.containerinstance.ContainerArgs(
        name=f"{prefix}-app",
        image=docker_image,
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
pulumi.export("resource_group_name", rg.name)
pulumi.export("container_group_name", container_group.name)
pulumi.export(
    "app_fqdn",
    container_group.ip_address.apply(
        lambda ip: ip.fqdn if ip and ip.fqdn else "not-assigned"
    )
)
