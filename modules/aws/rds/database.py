"""AWS RDS Database Module."""
import pulumi
import pulumi_aws as aws


class RdsDatabaseArgs:
    def __init__(self,
                 name: str,
                 vpc_id: pulumi.Input[str],
                 subnet_ids: pulumi.Input[list],
                 instance_class: str = "db.t3.micro",
                 allocated_storage: int = 20,
                 engine: str = "postgres",
                 engine_version: str = "13.7",
                 database_name: str = "appdb",
                 username: str = "admin",
                 multi_az: bool = False,
                 backup_retention_period: int = 7,
                 storage_encrypted: bool = True):
        self.name = name
        self.vpc_id = vpc_id
        self.subnet_ids = subnet_ids
        self.instance_class = instance_class
        self.allocated_storage = allocated_storage
        self.engine = engine
        self.engine_version = engine_version
        self.database_name = database_name
        self.username = username
        self.multi_az = multi_az
        self.backup_retention_period = backup_retention_period
        self.storage_encrypted = storage_encrypted


class RdsDatabase(pulumi.ComponentResource):
    def __init__(self, name: str, args: RdsDatabaseArgs, opts: pulumi.ResourceOptions = None):
        super().__init__("modules:aws:RdsDatabase", name, {}, opts)
        
        # Database Subnet Group
        subnet_group = aws.rds.SubnetGroup(
            f"{name}-subnet-group",
            subnet_ids=args.subnet_ids,
            tags={
                "Name": f"{args.name}-subnet-group",
                "ManagedBy": "pulumi"
            },
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Security Group
        security_group = aws.ec2.SecurityGroup(
            f"{name}-security-group",
            vpc_id=args.vpc_id,
            description=f"Security group for {args.name} RDS instance",
            ingress=[aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=5432,
                to_port=5432,
                cidr_blocks=["10.0.0.0/8"]  # Allow from VPC
            )],
            tags={
                "Name": f"{args.name}-security-group",
                "ManagedBy": "pulumi"
            },
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Database Instance
        self.instance = aws.rds.Instance(
            f"{name}-instance",
            identifier=args.name,
            instance_class=args.instance_class,
            allocated_storage=args.allocated_storage,
            engine=args.engine,
            engine_version=args.engine_version,
            db_name=args.database_name,
            username=args.username,
            password=pulumi.Config().require_secret("dbPassword"),
            db_subnet_group_name=subnet_group.name,
            vpc_security_group_ids=[security_group.id],
            multi_az=args.multi_az,
            backup_retention_period=args.backup_retention_period,
            storage_encrypted=args.storage_encrypted,
            skip_final_snapshot=True,
            deletion_protection=False,  # Set to True for production
            tags={
                "Name": args.name,
                "ManagedBy": "pulumi"
            },
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Export outputs
        self.register_outputs({
            "instance": self.instance,
            "endpoint": self.instance.endpoint,
            "username": self.instance.username
        })