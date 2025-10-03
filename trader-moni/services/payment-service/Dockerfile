FROM openjdk:17-jdk-slim AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
COPY .mvn ./.mvn
COPY mvnw ./mvnw
RUN ./mvnw clean package -DskipTests

FROM gcr.io/distroless/java17-debian11
COPY --from=builder /app/target/*.jar /app.jar
EXPOSE 8082
CMD ["/app.jar"]