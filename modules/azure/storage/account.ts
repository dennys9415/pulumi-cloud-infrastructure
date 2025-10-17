import * as pulumi from "@pulumi/pulumi";
import * as azure from "@pulumi/azure-native";

export interface StorageAccountArgs {
    resourceGroupName: pulumi.Input<string>;
    location: pulumi.Input<string>;
    accountTier?: string;
    accountReplicationType?: string;
    enableHttpsTrafficOnly?: boolean;
}

export class StorageAccount extends pulumi.ComponentResource {
    public account: azure.storage.StorageAccount;

    constructor(name: string, args: StorageAccountArgs, opts?: pulumi.ComponentResourceOptions) {
        super("modules:azure:StorageAccount", name, {}, opts);

        // Create Storage Account
        this.account = new azure.storage.StorageAccount(name, {
            resourceGroupName: args.resourceGroupName,
            location: args.location,
            kind: "StorageV2",
            sku: {
                name: `${args.accountTier || "Standard"}_${args.accountReplicationType || "LRS"}`,
            },
            enableHttpsTrafficOnly: args.enableHttpsTrafficOnly ?? true,
            accessTier: "Hot",
        }, { parent: this });

        // Create Blob Container
        const container = new azure.storage.BlobContainer("blob-container", {
            resourceGroupName: args.resourceGroupName,
            accountName: this.account.name,
            containerName: "data",
            publicAccess: "None",
        }, { parent: this });

        this.registerOutputs({
            account: this.account,
            container: container,
        });
    }
}