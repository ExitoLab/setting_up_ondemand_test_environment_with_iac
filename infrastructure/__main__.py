import pulumi
import pulumi_azure_native as azure

# Load Pulumi stack config
config = pulumi.Config()
location = config.get("azure:location") or "eastus"
env = config.get("azure:env") or "dev"

prefix = f"qa-{env}"
rg_name = f"{prefix}-rg"
aci_name = f"{prefix}-aci"

# --- Try to re-use existing Resource Group ---
try:
    existing_rg = azure.resources.get_resource_group(resource_group_name=rg_name)
    rg_name_out = existing_rg.name
except Exception:
    rg = azure.resources.ResourceGroup(
        rg_name,
        resource_group_name=rg_name,
        location=location
    )
    rg_name_out = rg.name

# Docker image passed from config (e.g. Pulumi.dev.yaml)
docker_image = config.get("docker:image") or "mcr.microsoft.com/azuredocs/aci-helloworld"

# --- Try to re-use existing Container Group ---
try:
    existing_aci = azure.containerinstance.get_container_group(
        resource_group_name=rg_name,
        container_group_name=aci_name,
    )
    container_group_name_out = existing_aci.name
    app_fqdn_out = existing_aci.ip_address.fqdn if existing_aci.ip_address else "not-assigned"
except Exception:
    container_group = azure.containerinstance.ContainerGroup(
        aci_name,
        resource_group_name=rg_name_out,
        location=location,
        os_type="Linux",
        containers=[
            azure.containerinstance.ContainerArgs(
                name=f"{prefix}-app",
                image=docker_image,
                resources=azure.containerinstance.ResourceRequirementsArgs(
                    requests=azure.containerinstance.ResourceRequestsArgs(
                        cpu=1.0,
                        memory_in_gb=1.5,
                    )
                ),
                ports=[azure.containerinstance.ContainerPortArgs(port=80)],
            )
        ],
        ip_address=azure.containerinstance.IpAddressArgs(
            ports=[azure.containerinstance.PortArgs(port=80, protocol="TCP")],
            type="Public",
        ),
    )
    container_group_name_out = container_group.name
    app_fqdn_out = container_group.ip_address.apply(
        lambda ip: ip.fqdn if ip and ip.fqdn else "not-assigned"
    )

# --- Export outputs ---
pulumi.export("resource_group_name", rg_name_out)
pulumi.export("container_group_name", container_group_name_out)
pulumi.export("app_fqdn", app_fqdn_out)
