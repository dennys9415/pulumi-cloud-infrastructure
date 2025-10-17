"""GCP Infrastructure as Code using Pulumi."""
import pulumi
import pulumi_gcp as gcp

from modules.gcp.gke import GkeCluster
from modules.gcp.cloud_sql import CloudSqlDatabase


class GcpInfrastructure:
    def __init__(self):
        self.config = pulumi.Config()
        self.stack = pulumi.get_stack()
        
        # Create VPC Network
        self.vpc = gcp.compute.Network(
            f"main-vpc-{self.stack}",
            name=f"main-vpc-{self.stack}",
            auto_create_subnetworks=False,
            description=f"Main VPC for {self.stack} environment",
            project=self.config.require("gcp:project")
        )
        
        # Create Subnets
        self.subnets = []
        regions = ["us-central1", "us-west1"]
        
        for i, region in enumerate(regions):
            subnet = gcp.compute.Subnetwork(
                f"subnet-{region}-{self.stack}",
                name=f"subnet-{region}-{self.stack}",
                ip_cidr_range=f"10.{i}.0.0/16",
                region=region,
                network=self.vpc.id,
                private_ip_google_access=True,
                project=self.config.require("gcp:project")
            )
            self.subnets.append(subnet)
        
        # Create GKE Cluster
        self.gke_cluster = GkeCluster(
            name=f"main-gke-{self.stack}",
            location="us-central1",
            network=self.vpc.id,
            subnetwork=self.subnets[0].id,
            min_node_count=self.config.get_int("minNodes") or 1,
            max_node_count=self.config.get_int("maxNodes") or 3,
            machine_type=self.config.get("machineType") or "e2-medium",
            enable_private_nodes=True
        )
        
        # Create Cloud SQL Database
        self.database = CloudSqlDatabase(
            name=f"main-db-{self.stack}",
            database_version="POSTGRES_13",
            tier=self.config.get("dbTier") or "db-f1-micro",
            disk_size=self.config.get_int("diskSize") or 20,
            availability_type="ZONAL" if self.stack == "dev" else "REGIONAL",
            backup_enabled=True,
            deletion_protection=self.stack == "production"
        )
        
        # Create Cloud Storage Bucket
        self.storage_bucket = gcp.storage.Bucket(
            f"app-bucket-{self.stack}",
            name=f"pulumi-app-{self.stack}-{pulumi.get_stack()}",
            location="US",
            force_destroy=self.stack != "production",
            uniform_bucket_level_access=True,
            versioning=gcp.storage.BucketVersioningArgs(
                enabled=self.stack == "production"
            ),
            encryption=gcp.storage.BucketEncryptionArgs(
                default_kms_key_name=""
            ),
            project=self.config.require("gcp:project")
        )
        
        # Export outputs
        self.export_outputs()
    
    def export_outputs(self):
        """Export important resource identifiers."""
        pulumi.export("vpc_name", self.vpc.name)
        pulumi.export("gke_cluster_name", self.gke_cluster.cluster.name)
        pulumi.export("gke_kubeconfig", self.gke_cluster.kubeconfig)
        pulumi.export("cloud_sql_instance_name", self.database.instance.name)
        pulumi.export("storage_bucket_name", self.storage_bucket.name)
        pulumi.export("subnet_names", [subnet.name for subnet in self.subnets])


# Create infrastructure
infra = GcpInfrastructure()