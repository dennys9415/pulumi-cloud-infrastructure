import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";
import * as aws from "@pulumi/aws";
import * as gcp from "@pulumi/gcp";

class KubernetesInfrastructure {
    private config: pulumi.Config;
    private stack: string;

    constructor() {
        this.config = new pulumi.Config();
        this.stack = pulumi.getStack();

        this.createKubernetesResources();
    }

    private createKubernetesResources() {
        // Create Namespaces
        const namespaces = [
            "app",
            "monitoring",
            "logging",
            "security",
            "ingress"
        ];

        for (const ns of namespaces) {
            new k8s.core.v1.Namespace(`${ns}-namespace`, {
                metadata: {
                    name: ns,
                    labels: {
                        environment: this.stack,
                        managedBy: "pulumi"
                    }
                }
            });
        }

        // Create NGINX Ingress Controller
        this.createNginxIngress();

        // Create Monitoring Stack (Prometheus + Grafana)
        this.createMonitoringStack();

        // Create Logging Stack (EFK)
        this.createLoggingStack();

        // Create Certificate Manager
        this.createCertificateManager();

        // Create Example Application
        this.createExampleApplication();
    }

    private createNginxIngress() {
        const ingressNamespace = "ingress";

        // NGINX Ingress Controller
        const nginx = new k8s.helm.v3.Chart("nginx-ingress", {
            chart: "nginx-ingress",
            version: "4.0.0",
            fetchOpts: {
                repo: "https://kubernetes.github.io/ingress-nginx",
            },
            namespace: ingressNamespace,
            values: {
                controller: {
                    replicaCount: this.stack === "production" ? 3 : 1,
                    service: {
                        type: "LoadBalancer",
                        annotations: this.getLoadBalancerAnnotations()
                    },
                    metrics: {
                        enabled: true
                    }
                }
            }
        });
    }

    private createMonitoringStack() {
        const monitoringNamespace = "monitoring";

        // Prometheus
        const prometheus = new k8s.helm.v3.Chart("prometheus", {
            chart: "prometheus",
            version: "15.0.0",
            fetchOpts: {
                repo: "https://prometheus-community.github.io/helm-charts",
            },
            namespace: monitoringNamespace,
            values: {
                alertmanager: {
                    enabled: true
                },
                pushgateway: {
                    enabled: false
                },
                server: {
                    persistentVolume: {
                        enabled: true,
                        size: "50Gi"
                    },
                    resources: {
                        limits: {
                            memory: "2Gi"
                        }
                    }
                }
            }
        });

        // Grafana
        const grafana = new k8s.helm.v3.Chart("grafana", {
            chart: "grafana",
            version: "6.0.0",
            fetchOpts: {
                repo: "https://grafana.github.io/helm-charts",
            },
            namespace: monitoringNamespace,
            values: {
                adminPassword: this.config.requireSecret("grafanaPassword"),
                persistence: {
                    enabled: true,
                    size: "10Gi"
                },
                datasources: {
                    datasources.yaml: {
                        apiVersion: 1,
                        datasources: [{
                            name: "Prometheus",
                            type: "prometheus",
                            url: "http://prometheus-server.monitoring.svc.cluster.local",
                            access: "proxy",
                            isDefault: true
                        }]
                    }
                }
            }
        });
    }

    private createLoggingStack() {
        const loggingNamespace = "logging";

        // Elasticsearch
        const elasticsearch = new k8s.helm.v3.Chart("elasticsearch", {
            chart: "elasticsearch",
            version: "7.0.0",
            fetchOpts: {
                repo: "https://helm.elastic.co",
            },
            namespace: loggingNamespace,
            values: {
                replicas: this.stack === "production" ? 3 : 1,
                minimumMasterNodes: this.stack === "production" ? 2 : 1,
                resources: {
                    requests: {
                        memory: "1Gi"
                    }
                }
            }
        });

        // Fluentd
        const fluentd = new k8s.helm.v3.Chart("fluentd", {
            chart: "fluentd",
            version: "2.0.0",
            fetchOpts: {
                repo: "https://fluent.github.io/helm-charts",
            },
            namespace: loggingNamespace,
            values: {
                resources: {
                    limits: {
                        memory: "512Mi"
                    }
                }
            }
        });

        // Kibana
        const kibana = new k8s.helm.v3.Chart("kibana", {
            chart: "kibana",
            version: "7.0.0",
            fetchOpts: {
                repo: "https://helm.elastic.co",
            },
            namespace: loggingNamespace,
            values: {
                replicas: 1,
                resources: {
                    limits: {
                        memory: "1Gi"
                    }
                }
            }
        });
    }

    private createCertificateManager() {
        // Cert Manager for TLS certificates
        const certManager = new k8s.helm.v3.Chart("cert-manager", {
            chart: "cert-manager",
            version: "1.0.0",
            fetchOpts: {
                repo: "https://charts.jetstack.io",
            },
            namespace: "security",
            values: {
                installCRDs: true,
                resources: {
                    limits: {
                        memory: "256Mi"
                    }
                }
            }
        });

        // Cluster Issuer
        const clusterIssuer = new k8s.apiextensions.CustomResource("cluster-issuer", {
            apiVersion: "cert-manager.io/v1",
            kind: "ClusterIssuer",
            metadata: {
                name: "letsencrypt-prod",
                namespace: "security"
            },
            spec: {
                acme: {
                    server: "https://acme-v02.api.letsencrypt.org/directory",
                    email: this.config.require("acmeEmail"),
                    privateKeySecretRef: {
                        name: "letsencrypt-prod"
                    },
                    solvers: [{
                        http01: {
                            ingress: {
                                class: "nginx"
                            }
                        }
                    }]
                }
            }
        }, { dependsOn: [certManager] });
    }

    private createExampleApplication() {
        const appNamespace = "app";

        // Example Deployment
        const deployment = new k8s.apps.v1.Deployment("example-app", {
            metadata: {
                name: "example-app",
                namespace: appNamespace,
                labels: {
                    app: "example-app"
                }
            },
            spec: {
                replicas: this.stack === "production" ? 3 : 1,
                selector: {
                    matchLabels: {
                        app: "example-app"
                    }
                },
                template: {
                    metadata: {
                        labels: {
                            app: "example-app"
                        }
                    },
                    spec: {
                        containers: [{
                            name: "app",
                            image: "nginx:alpine",
                            ports: [{
                                containerPort: 80
                            }],
                            resources: {
                                requests: {
                                    memory: "64Mi",
                                    cpu: "50m"
                                },
                                limits: {
                                    memory: "128Mi",
                                    cpu: "100m"
                                }
                            }
                        }]
                    }
                }
            }
        });

        // Service
        const service = new k8s.core.v1.Service("example-service", {
            metadata: {
                name: "example-service",
                namespace: appNamespace
            },
            spec: {
                selector: {
                    app: "example-app"
                },
                ports: [{
                    port: 80,
                    targetPort: 80
                }],
                type: "ClusterIP"
            }
        });

        // Ingress
        const ingress = new k8s.networking.v1.Ingress("example-ingress", {
            metadata: {
                name: "example-ingress",
                namespace: appNamespace,
                annotations: {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                }
            },
            spec: {
                tls: [{
                    hosts: ["example.app.com"],
                    secretName: "example-tls"
                }],
                rules: [{
                    host: "example.app.com",
                    http: {
                        paths: [{
                            path: "/",
                            pathType: "Prefix",
                            backend: {
                                service: {
                                    name: service.metadata.name,
                                    port: {
                                        number: 80
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        });
    }

    private getLoadBalancerAnnotations(): { [key: string]: string } {
        const annotations: { [key: string]: string } = {};

        if (this.config.get("cloudProvider") === "aws") {
            annotations["service.beta.kubernetes.io/aws-load-balancer-type"] = "nlb";
            annotations["service.beta.kubernetes.io/aws-load-balancer-ssl-cert"] = 
                this.config.require("awsCertificateArn");
        } else if (this.config.get("cloudProvider") === "gcp") {
            annotations["networking.gke.io/load-balancer-type"] = "Internal";
        }

        return annotations;
    }

    // Export outputs
    private exportOutputs() {
        pulumi.export("kubernetesNamespace", "app");
        pulumi.export("monitoringEnabled", true);
        pulumi.export("loggingEnabled", true);
        pulumi.export("certManagerEnabled", true);
    }
}

// Create Kubernetes infrastructure
new KubernetesInfrastructure();