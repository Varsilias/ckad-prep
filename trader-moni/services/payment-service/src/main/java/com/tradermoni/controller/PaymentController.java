package com.tradermoni.payment.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/payments")
public class PaymentController {
    
    @Value("${service.name:payment-service}")
    private String serviceName;
    
    @Value("${service.version:1.0.0}")
    private String serviceVersion;
    
    private final Map<String, Payment> payments = new HashMap<>();
    
    @PostMapping
    public Payment processPayment(@RequestBody PaymentRequest request) {
        Payment payment = new Payment();
        payment.setId("payment-" + System.currentTimeMillis());
        payment.setAmount(request.getAmount());
        payment.setStatus("processed");
        payment.setCreatedAt(LocalDateTime.now());
        
        payments.put(payment.getId(), payment);
        return payment;
    }
    
    @GetMapping("/{id}")
    public Payment getPayment(@PathVariable String id) {
        return payments.get(id);
    }
    
    static class Payment {
        private String id;
        private double amount;
        private String status;
        private LocalDateTime createdAt;
        
        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public double getAmount() { return amount; }
        public void setAmount(double amount) { this.amount = amount; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public LocalDateTime getCreatedAt() { return createdAt; }
        public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    }
    
    static class PaymentRequest {
        private double amount;
        private String orderId;
        
        public double getAmount() { return amount; }
        public void setAmount(double amount) { this.amount = amount; }
        public String getOrderId() { return orderId; }
        public void setOrderId(String orderId) { this.orderId = orderId; }
    }
}