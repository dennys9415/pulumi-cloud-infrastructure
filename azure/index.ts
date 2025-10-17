import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";
import * as k8s from "@pulumi/kubernetes";

import { AksCluster } from "./modules/azure/aks";
import { StorageAccount } from "./modules/azure/storage";

class AzureInfrastructure {
    private config: pulumi.Config;
    private stack: string;

    constructor() {
        this.config = new pulumi.Config();
        this.stack = pulumi.getStack();

        this.createInfrastructure();
    }

    private createInfrastructure() {
        // Create Resource Group
        const resourceGroup = new azure.resources.ResourceGroup(`rg-${this.stack}`, {
            resourceGroupName: `pulumi-${this.stack}-rg`,
            location: this.config.get("location") || "EastUS",
        });

        // Create AKS Cluster
        const aksCluster = new AksCluster(`aks-${this.stack}`, {
            resourceGroupName: resourceGroup.name,
            location: resourceGroup.location,
            nodeCount: this.config.getNumber("nodeCount") || (this.stack === "dev" ? 1 : 3),
            vmSize: this.config.get("vmSize") || (this.stack === "dev" ? "Standard_D2s_v3" : "Standard_D4s_v3"),
            enableAutoScaling: this.stack !== "dev",
            minCount: this.config.getNumber("minCount") || 1,
            maxCount: this.config.getNumber("maxCount") || (this.stack === "dev" ? 3 : 10),
            kubernetesVersion: this.config.get("kubernetesVersion") || "1.27",
        });

        // Create Storage Account
        const storageAccount = new StorageAccount(`sa${this.stack}`, {
            resourceGroupName: resourceGroup.name,
            location: resourceGroup.location,
            accountTier: this.stack === "production" ? "Premium" : "Standard",
            accountReplicationType: this.stack === "production" ? "LRS" : "GRS",
        });

        // Create PostgreSQL Server
        const postgresql = new azure.dbforpostgresql.Server(`psql-${this.stack}`, {
            resourceGroupName: resourceGroup.name,
            serverName: `pulumi-psql-${this.stack}`,
            location: resourceGroup.location,
            properties: {
                administratorLogin: this.config.get("dbAdmin") || "psqladmin",
                administratorLoginPassword: this.config.requireSecret("dbPassword"),
                storageProfile: {
                    storageMB: this.stack === "dev" ? 5120 : 102400,
                    backupRetentionDays: this.stack === "production" ? 7 : 3,
                },
                sslEnforcement: azure.dbforpostgresql.SslEnforcementEnum.Enabled,
                createMode: "Default",
                version: "13",
            },
            sku: {
                name: this.stack === "dev" ? "B_Gen5_1" : "GP_Gen5_4",
                tier: this.stack === "dev" ? "Basic" : "GeneralPurpose",
            },
        });

        // Create Virtual Network
        const virtualNetwork = new azure.network.VirtualNetwork(`vnet-${this.stack}`, {
            resourceGroupName: resourceGroup.name,
            location: resourceGroup.location,
            virtualNetworkName: `vnet-${this.stack}`,
            addressSpace: {
                addressPrefixes: ["10.1.0.0/16"],
            },
        });

        // Create Subnets
        const subnet1 = new azure.network.Subnet(`subnet-1-${this.stack}`, {
            resourceGroupName: resourceGroup.name,
            virtualNetworkName: virtualNetwork.name,
            addressPrefix: "10.1.1.0/24",
            subnetName: `subnet-1-${this.stack}`,
        });

        const subnet2 = new azure.network.Subnet(`subnet-2-${this.stack}`, {
            resourceGroupName: resourceGroup.name,
            virtualNetworkName: virtualNetwork.name,
            addressPrefix: "10.1.2.0/24",
            subnetName: `subnet-2-${this.stack}`,
        });

        // Export outputs
        pulumi.all([aksCluster.cluster.name, aksCluster.kubeconfig]).apply(([name, kubeconfig]) => {
            pulumi.export("aksClusterName", name);
            pulumi.export("kubeconfig", kubeconfig);
        });

        pulumi.export("resourceGroupName", resourceGroup.name);
        pulumi.export("storageAccountName", storageAccount.account.name);
        pulumi.export("postgresqlFqdn", postgresql.fullyQualifiedDomainName);
        pulumi.export("virtualNetworkName", virtualNetwork.name);
    }
}

// Create infrastructure
new AzureInfrastructure();