"""AWS Infrastructure as Code using Pulumi."""
import pulumi
import pulumi_aws as aws

from modules.aws.vpc import Vpc
from modules.aws.eks import EksCluster
from modules.aws.rds import RdsDatabase


class AwsInfrastructure:
    def __init__(self):
        self.config = pulumi.Config()
        self.stack = pulumi.get_stack()
        
        # Create VPC
        self.vpc = Vpc(
            name=f"main-vpc-{self.stack}",
            cidr_block=self.config.get("vpcCidrBlock") or "10.0.0.0/16",
            enable_nat_gateway=True,
            single_nat_gateway=self.stack != "production",
            tags={
                "Environment": self.stack,
                "Project": "pulumi-cloud-infrastructure",
                "ManagedBy": "pulumi"
            }
        )
        
        # Create EKS Cluster
        self.eks_cluster = EksCluster(
            name=f"main-eks-{self.stack}",
            vpc_id=self.vpc.vpc_id,
            private_subnet_ids=self.vpc.private_subnet_ids,
            public_subnet_ids=self.vpc.public_subnet_ids,
            instance_types=["t3.medium"],
            min_size=self.config.get_int("minNodes") or 1,
            max_size=self.config.get_int("maxNodes") or 3,
            desired_size=self.config.get_int("desiredNodes") or 1
        )
        
        # Create RDS Database
        self.database = RdsDatabase(
            name=f"main-db-{self.stack}",
            vpc_id=self.vpc.vpc_id,
            subnet_ids=self.vpc.private_subnet_ids,
            instance_class=self.config.get("databaseInstanceClass") or "db.t3.micro",
            allocated_storage=self.config.get_int("allocatedStorage") or 20,
            multi_az=self.stack == "production",
            backup_retention_period=7 if self.stack == "production" else 3
        )
        
        # Create S3 Bucket for application data
        self.app_bucket = aws.s3.BucketV2(
            f"app-bucket-{self.stack}",
            bucket=f"pulumi-app-{self.stack}-{pulumi.get_stack()}",
            force_destroy=self.stack != "production",
            tags={
                "Environment": self.stack,
                "Project": "pulumi-cloud-infrastructure"
            }
        )
        
        # Enable versioning for production
        if self.stack == "production":
            aws.s3.BucketVersioningV2(
                f"app-bucket-versioning-{self.stack}",
                bucket=self.app_bucket.id,
                versioning_configuration=aws.s3.BucketVersioningV2VersioningConfigurationArgs(
                    status="Enabled"
                )
            )
        
        # Enable server-side encryption
        aws.s3.BucketServerSideEncryptionConfigurationV2(
            f"app-bucket-encryption-{self.stack}",
            bucket=self.app_bucket.id,
            rules=[aws.s3.BucketServerSideEncryptionConfigurationV2RuleArgs(
                apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationV2RuleApplyServerSideEncryptionByDefaultArgs(
                    sse_algorithm="AES256"
                )
            )]
        )
        
        # Export outputs
        self.export_outputs()
    
    def export_outputs(self):
        """Export important resource identifiers."""
        pulumi.export("vpc_id", self.vpc.vpc_id)
        pulumi.export("eks_cluster_name", self.eks_cluster.cluster.name)
        pulumi.export("eks_kubeconfig", self.eks_cluster.kubeconfig)
        pulumi.export("rds_endpoint", self.database.instance.endpoint)
        pulumi.export("s3_bucket_name", self.app_bucket.bucket)
        pulumi.export("private_subnet_ids", self.vpc.private_subnet_ids)
        pulumi.export("public_subnet_ids", self.vpc.public_subnet_ids)


# Create infrastructure
infra = AwsInfrastructure()