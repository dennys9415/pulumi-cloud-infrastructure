"""Tests for AWS infrastructure."""
import unittest
import pulumi
import pulumi_aws as aws


class TestAwsInfrastructure(unittest.TestCase):
    """Test cases for AWS infrastructure."""
    
    def test_vpc_creation(self):
        """Test VPC creation with proper CIDR range."""
        from modules.aws.vpc import Vpc, VpcArgs
        
        # Mock Pulumi runtime
        pulumi.runtime.set_mocks(
            MockAwsProvider(),
            project='test',
            stack='test',
            preview=False
        )
        
        # Create VPC
        vpc_args = VpcArgs(
            name="test-vpc",
            cidr_block="10.0.0.0/16",
            enable_nat_gateway=True
        )
        vpc = Vpc("test-vpc", vpc_args)
        
        # Verify VPC properties
        self.assertEqual(vpc.vpc_id, "vpc-12345")
        self.assertEqual(len(vpc.public_subnet_ids), 2)
        self.assertEqual(len(vpc.private_subnet_ids), 2)
    
    def test_eks_cluster_creation(self):
        """Test EKS cluster creation."""
        from modules.aws.eks import EksCluster, EksClusterArgs
        
        pulumi.runtime.set_mocks(
            MockAwsProvider(),
            project='test',
            stack='test',
            preview=False
        )
        
        eks_args = EksClusterArgs(
            name="test-eks",
            vpc_id="vpc-12345",
            private_subnet_ids=["subnet-1", "subnet-2"],
            min_size=1,
            max_size=3
        )
        eks = EksCluster("test-eks", eks_args)
        
        self.assertIsNotNone(eks.cluster)
        self.assertIsNotNone(eks.kubeconfig)
    
    def test_rds_database_creation(self):
        """Test RDS database creation."""
        from modules.aws.rds import RdsDatabase, RdsDatabaseArgs
        
        pulumi.runtime.set_mocks(
            MockAwsProvider(),
            project='test',
            stack='test',
            preview=False
        )
        
        rds_args = RdsDatabaseArgs(
            name="test-db",
            vpc_id="vpc-12345",
            subnet_ids=["subnet-1", "subnet-2"],
            instance_class="db.t3.micro"
        )
        rds = RdsDatabase("test-db", rds_args)
        
        self.assertIsNotNone(rds.instance)


class MockAwsProvider:
    """Mock AWS provider for testing."""
    
    def call(self, token, args, provider):
        return {}
    
    def new_resource(self, token, name, inputs, provider, id_):
        if token == "aws:ec2/vpc:Vpc":
            return {"id": "vpc-12345"}
        elif token == "aws:ec2/subnet:Subnet":
            return {"id": f"subnet-{name}"}
        elif token == "aws:eks/cluster:Cluster":
            return {
                "id": "cluster-12345",
                "name": name,
                "endpoint": "https://cluster.example.com",
                "certificate_authority": {"data": "test-ca"}
            }
        elif token == "aws:rds/instance:Instance":
            return {
                "id": "db-12345",
                "endpoint": "db.example.com:5432",
                "username": "admin"
            }
        return {}


if __name__ == '__main__':
    unittest.main()