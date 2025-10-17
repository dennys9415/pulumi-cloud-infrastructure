"""AWS EKS Cluster Module."""
import pulumi
import pulumi_aws as aws
import pulumi_kubernetes as k8s


class EksClusterArgs:
    def __init__(self,
                 name: str,
                 vpc_id: pulumi.Input[str],
                 private_subnet_ids: pulumi.Input[list],
                 public_subnet_ids: pulumi.Input[list] = None,
                 instance_types: list = None,
                 min_size: int = 1,
                 max_size: int = 3,
                 desired_size: int = 1,
                 kubernetes_version: str = "1.27",
                 enable_cluster_logging: bool = True):
        self.name = name
        self.vpc_id = vpc_id
        self.private_subnet_ids = private_subnet_ids
        self.public_subnet_ids = public_subnet_ids or []
        self.instance_types = instance_types or ["t3.medium"]
        self.min_size = min_size
        self.max_size = max_size
        self.desired_size = desired_size
        self.kubernetes_version = kubernetes_version
        self.enable_cluster_logging = enable_cluster_logging


class EksCluster(pulumi.ComponentResource):
    def __init__(self, name: str, args: EksClusterArgs, opts: pulumi.ResourceOptions = None):
        super().__init__("modules:aws:EksCluster", name, {}, opts)
        
        # EKS Cluster Role
        cluster_role = aws.iam.Role(
            f"{name}-cluster-role",
            assume_role_policy=pulumi.Output.json_dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "eks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            }),
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
                "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
            ],
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # EKS Cluster
        self.cluster = aws.eks.Cluster(
            f"{name}-cluster",
            role_arn=cluster_role.arn,
            version=args.kubernetes_version,
            vpc_config=aws.eks.ClusterVpcConfigArgs(
                subnet_ids=args.private_subnet_ids + args.public_subnet_ids,
                endpoint_private_access=True,
                endpoint_public_access=True
            ),
            enabled_cluster_log_types=[
                "api", "audit", "authenticator", "controllerManager", "scheduler"
            ] if args.enable_cluster_logging else [],
            tags={
                "Name": args.name,
                "ManagedBy": "pulumi"
            },
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Node Group Role
        node_group_role = aws.iam.Role(
            f"{name}-nodegroup-role",
            assume_role_policy=pulumi.Output.json_dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            }),
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
                "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
            ],
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Node Group
        self.node_group = aws.eks.NodeGroup(
            f"{name}-nodegroup",
            cluster_name=self.cluster.name,
            node_role_arn=node_group_role.arn,
            subnet_ids=args.private_subnet_ids,
            scaling_config=aws.eks.NodeGroupScalingConfigArgs(
                desired_size=args.desired_size,
                min_size=args.min_size,
                max_size=args.max_size
            ),
            instance_types=args.instance_types,
            disk_size=20,
            tags={
                "Name": f"{args.name}-nodes",
                "ManagedBy": "pulumi"
            },
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.cluster]
            )
        )
        
        # Kubeconfig
        self.kubeconfig = pulumi.Output.all(
            self.cluster.name,
            self.cluster.endpoint,
            self.cluster.certificate_authority.data
        ).apply(lambda args: """
apiVersion: v1
clusters:
- cluster:
    server: {1}
    certificate-authority-data: {2}
  name: {0}
contexts:
- context:
    cluster: {0}
    user: {0}
  name: {0}
current-context: {0}
kind: Config
preferences: {{}}
users:
- name: {0}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "{0}"
""".format(args[0], args[1], args[2]))
        
        # Kubernetes provider
        self.k8s_provider = k8s.Provider(
            f"{name}-k8s-provider",
            kubeconfig=self.kubeconfig,
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Export outputs
        self.register_outputs({
            "cluster": self.cluster,
            "node_group": self.node_group,
            "kubeconfig": self.kubeconfig,
            "k8s_provider": self.k8s_provider
        })