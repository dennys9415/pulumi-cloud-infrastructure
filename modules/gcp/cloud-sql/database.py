"""GCP Cloud SQL Database Module."""
import pulumi
import pulumi_gcp as gcp


class CloudSqlDatabaseArgs:
    def __init__(self,
                 name: str,
                 database_version: str = "POSTGRES_13",
                 tier: str = "db-f1-micro",
                 disk_size: int = 20,
                 availability_type: str = "ZONAL",
                 backup_enabled: bool = True,
                 deletion_protection: bool = False):
        self.name = name
        self.database_version = database_version
        self.tier = tier
        self.disk_size = disk_size
        self.availability_type = availability_type
        self.backup_enabled = backup_enabled
        self.deletion_protection = deletion_protection


class CloudSqlDatabase(pulumi.ComponentResource):
    def __init__(self, name: str, args: CloudSqlDatabaseArgs, opts: pulumi.ResourceOptions = None):
        super().__init__("modules:gcp:CloudSqlDatabase", name, {}, opts)
        
        # Cloud SQL Instance
        self.instance = gcp.sql.DatabaseInstance(
            f"{name}-instance",
            name=args.name,
            database_version=args.database_version,
            region="us-central1",
            settings=gcp.sql.DatabaseInstanceSettingsArgs(
                tier=args.tier,
                disk_size=args.disk_size,
                disk_type="PD_SSD",
                availability_type=args.availability_type,
                backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
                    enabled=args.backup_enabled,
                    start_time="02:00"
                ),
                ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
                    ipv4_enabled=True,
                    require_ssl=True
                )
            ),
            deletion_protection=args.deletion_protection,
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Database
        database = gcp.sql.Database(
            f"{name}-database",
            name="appdb",
            instance=self.instance.name,
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # User
        user = gcp.sql.User(
            f"{name}-user",
            name="appuser",
            instance=self.instance.name,
            password=pulumi.Config().require_secret("dbPassword"),
            opts=pulumi.ResourceOptions(parent=self)
        )
        
        # Export outputs
        self.register_outputs({
            "instance": self.instance,
            "database": database,
            "user": user
        })