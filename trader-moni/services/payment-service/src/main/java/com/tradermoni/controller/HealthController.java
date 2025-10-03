package com.tradermoni.payment.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/health")
public class HealthController {

    @Value("${service.name:payment-service}")
    private String serviceName;
    
    @Value("${service.version:1.0.0}")
    private String serviceVersion;

    @Value("${service.environment:development}")
    private String environment;

    @GetMapping
    public Health getHealth() {
        Health health = new Health();
        
        health.setService(serviceName);
        health.setVersion(serviceVersion);
        health.setStatus("healthy");
        health.setTimestamp(LocalDateTime.now());
        health.setEnvironment(environment);

        return health;
    }

    static class Health {
        private String service;
        private String version;
        private String status;
        private LocalDateTime timestamp;
        private String environment;
        
        // Getters and setters
        public String getService() { return service; }
        public void setService(String service) { this.service = service; }
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public String getEnvironment() { return environment; }
        public void setEnvironment(String environment) { this.environment = environment; }
        public LocalDateTime getTimestamp() { return timestamp; }
        public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
    }
}