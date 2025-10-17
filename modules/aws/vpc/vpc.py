"""AWS VPC Module."""
import pulumi
import pulumi_aws as aws


class VpcArgs:
    def __init__(self,
                 name: str,
                 cidr_block: str = "10.0.0.0/16",
                 enable_nat_gateway: bool = True,
                 single_nat_gateway: bool = False,
                 enable_dns_hostnames: bool = True,
                 enable_dns_support: bool = True,
                 tags: dict = None):
        self.name = name
        self.cidr_block = cidr_block
        self.enable_nat_gateway = enable_nat_gateway
        self.single_nat_gateway = single_nat_gateway
        self.enable_dns_hostnames = enable_dns_hostnames
        self.enable_dns_support = enable_dns_support
        self.tags = tags or {}


class Vpc(pulumi.ComponentResource):
    def __init__(self, name: str, args: VpcArgs, opts: pulumi.ResourceOptions = None):
        super().__init__("modules:aws:Vpc", name, {}, opts)
        
        # Base tags
        base_tags = {
            "Name": f"{args.name}-vpc",
            "Environment": "production",
            "ManagedBy": "pulumi",
            "Project": "cloud-infrastructure"
        }
        base_tags.update(args.tags)
        
        self.vpc = aws.ec2.Vpc(
            f"{name}-vpc",
            cidr_block=args.cidr_block,
            enable_dns_hostnames=args.enable_dns_hostnames,
            enable_dns_support=args.enable_dns_support,
            tags=base_tags,
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create Internet Gateway
        self.igw = aws.ec2.InternetGateway(
            f"{name}-igw",
            vpc_id=self.vpc.id,
            tags={**base_tags, "Name": f"{args.name}-igw"},
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Create subnets
        self.public_subnets = []
        self.private_subnets = []
        
        # Create 2 public and 2 private subnets across 2 AZs
        availability_zones = ["a", "b"]
        
        for i, az in enumerate(availability_zones):
            # Public Subnet
            public_subnet = aws.ec2.Subnet(
                f"{name}-public-{az}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{i}.0/24",
                availability_zone=f"{pulumi.get_region()}{az}",
                map_public_ip_on_launch=True,
                tags={**base_tags, "Name": f"{args.name}-public-{az}"},
                opts=pulumi.ResourceOptions(parent=self)
            )
            self.public_subnets.append(public_subnet)
            
            # Private Subnet
            private_subnet = aws.ec2.Subnet(
                f"{name}-private-{az}",
                vpc_id=self.vpc.id,
                cidr_block=f"10.0.{i + 10}.0/24",
                availability_zone=f"{pulumi.get_region()}{az}",
                tags={**base_tags, "Name": f"{args.name}-private-{az}"},
                opts=pulumi.ResourceOptions(parent=self)
            )
            self.private_subnets.append(private_subnet)
        
        # Create Route Tables
        self.public_route_table = aws.ec2.RouteTable(
            f"{name}-public-rt",
            vpc_id=self.vpc.id,
            routes=[aws.ec2.RouteTableRouteArgs(
                cidr_block="0.0.0.0/0",
                gateway_id=self.igw.id,
            )],
            tags={**base_tags, "Name": f"{args.name}-public-rt"},
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Associate public subnets with public route table
        for i, subnet in enumerate(self.public_subnets):
            aws.ec2.RouteTableAssociation(
                f"{name}-public-rta-{i}",
                subnet_id=subnet.id,
                route_table_id=self.public_route_table.id,
                opts=pulumi.ResourceOptions(parent=self)
            )
        
        # Create NAT Gateway if enabled
        if args.enable_nat_gateway:
            self.nat_gateways = []
            
            for i, subnet in enumerate(self.public_subnets):
                if args.single_nat_gateway and i > 0:
                    # Reuse first NAT Gateway
                    continue
                    
                eip = aws.ec2.Eip(
                    f"{name}-nat-eip-{i}",
                    domain="vpc",
                    tags={**base_tags, "Name": f"{args.name}-nat-eip-{i}"},
                    opts=pulumi.ResourceOptions(parent=self)
                )
                
                nat_gw = aws.ec2.NatGateway(
                    f"{name}-nat-{i}",
                    allocation_id=eip.id,
                    subnet_id=subnet.id,
                    tags={**base_tags, "Name": f"{args.name}-nat-{i}"},
                    opts=pulumi.ResourceOptions(
                        parent=self,
                        depends_on=[self.igw]  # Ensure IGW exists first
                    )
                )
                self.nat_gateways.append(nat_gw)
            
            # Create private route tables with NAT Gateway routes
            self.private_route_tables = []
            for i, subnet in enumerate(self.private_subnets):
                nat_gw_index = 0 if args.single_nat_gateway else i
                
                private_rt = aws.ec2.RouteTable(
                    f"{name}-private-rt-{i}",
                    vpc_id=self.vpc.id,
                    routes=[aws.ec2.RouteTableRouteArgs(
                        cidr_block="0.0.0.0/0",
                        nat_gateway_id=self.nat_gateways[nat_gw_index].id,
                    )],
                    tags={**base_tags, "Name": f"{args.name}-private-rt-{i}"},
                    opts=pulumi.ResourceOptions(parent=self)
                )
                
                aws.ec2.RouteTableAssociation(
                    f"{name}-private-rta-{i}",
                    subnet_id=subnet.id,
                    route_table_id=private_rt.id,
                    opts=pulumi.ResourceOptions(parent=self)
                )
                self.private_route_tables.append(private_rt)
        
        # Export outputs
        self.vpc_id = self.vpc.id
        self.public_subnet_ids = [subnet.id for subnet in self.public_subnets]
        self.private_subnet_ids = [subnet.id for subnet in self.private_subnets]
        
        self.register_outputs({
            "vpc_id": self.vpc_id,
            "public_subnet_ids": self.public_subnet_ids,
            "private_subnet_ids": self.private_subnet_ids,
        })