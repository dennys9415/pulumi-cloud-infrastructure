"""GCP GKE Cluster Module."""
import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s


class GkeClusterArgs:
    def __init__(self,
                 name: str,
                 location: str,
                 network: pulumi.Input[str],
                 subnetwork: pulumi.Input[str],
                 min_node_count: int = 1,
                 max_node_count: int = 3,
                 machine_type: str = "e2-medium",
                 enable_private_nodes: bool = True,
                 kubernetes_version: str = "1.27"):
        self.name = name
        self.location = location
        self.network = network
        self.subnetwork = subnetwork
        self.min_node_count = min_node_count
        self.max_node_count = max_node_count
        self.machine_type = machine_type
        self.enable_private_nodes = enable_private_nodes
        self.kubernetes_version = kubernetes_version


class GkeCluster(pulumi.ComponentResource):
    def __init__(self, name: str, args: GkeClusterArgs, opts: pulumi.ResourceOptions = None):
        super().__init__("modules:gcp:GkeCluster", name, {}, opts)
        
        # GKE Cluster
        self.cluster = gcp.container.Cluster(
            f"{name}-cluster",
            name=args.name,
            location=args.location,
            network=args.network,
            subnetwork=args.subnetwork,
            min_master_version=args.kubernetes_version,
            initial_node_count=1,
            remove_default_node_pool=True,
            networking_mode="VPC_NATIVE",
            private_cluster_config=gcp.container.ClusterPrivateClusterConfigArgs(
                enable_private_nodes=args.enable_private_nodes,
                enable_private_endpoint=False,
                master_ipv4_cidr_block="172.16.0.0/28"
            ) if args.enable_private_nodes else None,
            ip_allocation_policy=gcp.container.ClusterIpAllocationPolicyArgs(
                cluster_ipv4_cidr_block="/16",
                services_ipv4_cidr_block="/22"
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Node Pool
        node_pool = gcp.container.NodePool(
            f"{name}-node-pool",
            name=f"{args.name}-node-pool",
            location=args.location,
            cluster=self.cluster.name,
            node_count=args.min_node_count,
            node_config=gcp.container.NodePoolNodeConfigArgs(
                preemptible=False,
                machine_type=args.machine_type,
                disk_size_gb=100,
                disk_type="pd-standard",
                oauth_scopes=[
                    "https://www.googleapis.com/auth/cloud-platform"
                ],
                tags=["gke-node", args.name]
            ),
            autoscaling=gcp.container.NodePoolAutoscalingArgs(
                min_node_count=args.min_node_count,
                max_node_count=args.max_node_count
            ),
            management=gcp.container.NodePoolManagementArgs(
                auto_repair=True,
                auto_upgrade=True
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.cluster]
            )
        )
        
        # Kubeconfig
        self.kubeconfig = pulumi.Output.all(
            self.cluster.name,
            self.cluster.endpoint,
            self.cluster.master_auth
        ).apply(lambda args: """
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {2}
    server: https://{1}
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
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl by following
        https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke
      provideClusterInfo: true
""".format(args[0], args[1], args[2]['cluster_ca_certificate']))
        
        # Kubernetes provider
        self.k8s_provider = k8s.Provider(
            f"{name}-k8s-provider",
            kubeconfig=self.kubeconfig,
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Export outputs
        self.register_outputs({
            "cluster": self.cluster,
            "node_pool": node_pool,
            "kubeconfig": self.kubeconfig,
            "k8s_provider": self.k8s_provider
        })