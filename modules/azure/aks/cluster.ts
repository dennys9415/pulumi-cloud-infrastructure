import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";
import * as k8s from "@pulumi/kubernetes";

export interface AksClusterArgs {
    resourceGroupName: pulumi.Input<string>;
    location: pulumi.Input<string>;
    nodeCount?: number;
    vmSize?: string;
    enableAutoScaling?: boolean;
    minCount?: number;
    maxCount?: number;
    kubernetesVersion?: string;
}

export class AksCluster extends pulumi.ComponentResource {
    public cluster: azure.containerservice.ManagedCluster;
    public kubeconfig: pulumi.Output<string>;
    public resourceGroupName: pulumi.Input<string>;

    constructor(name: string, args: AksClusterArgs, opts?: pulumi.ComponentResourceOptions) {
        super("modules:azure:AksCluster", name, {}, opts);

        this.resourceGroupName = args.resourceGroupName;

        // Create AKS Cluster
        this.cluster = new azure.containerservice.ManagedCluster(name, {
            resourceGroupName: args.resourceGroupName,
            location: args.location,
            identity: {
                type: azure.containerservice.ResourceIdentityType.SystemAssigned,
            },
            kubernetesVersion: args.kubernetesVersion || "1.27",
            dnsPrefix: name,
            agentPoolProfiles: [{
                name: "nodepool",
                count: args.nodeCount || 3,
                vmSize: args.vmSize || "Standard_D2s_v3",
                osType: "Linux",
                mode: "System",
                enableAutoScaling: args.enableAutoScaling || false,
                minCount: args.minCount,
                maxCount: args.maxCount,
                type: "VirtualMachineScaleSets",
            }],
            linuxProfile: {
                adminUsername: "azureuser",
                ssh: {
                    publicKeys: [{
                        keyData: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...", // Replace with actual SSH key
                    }],
                },
            },
            networkProfile: {
                networkPlugin: "azure",
                networkPolicy: "azure",
                serviceCidr: "10.0.0.0/16",
                dnsServiceIp: "10.0.0.10",
                dockerBridgeCidr: "172.17.0.1/16",
            },
            enableRBAC: true,
        }, { parent: this });

        // Get kubeconfig
        this.kubeconfig = pulumi.all([this.cluster.name, args.resourceGroupName]).apply(
            ([clusterName, resourceGroupName]) => {
                return azure.containerservice.listManagedClusterUserCredentials({
                    resourceGroupName: resourceGroupName,
                    resourceName: clusterName,
                }).then(creds => {
                    const kubeconfig = Buffer.from(creds.kubeconfigs[0].value, 'base64').toString();
                    return kubeconfig;
                });
            }
        );

        // Kubernetes provider
        const k8sProvider = new k8s.Provider(`${name}-k8s-provider`, {
            kubeconfig: this.kubeconfig,
        }, { parent: this });

        this.registerOutputs({
            cluster: this.cluster,
            kubeconfig: this.kubeconfig,
            k8sProvider: k8sProvider,
        });
    }
}