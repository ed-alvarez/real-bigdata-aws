FROM python:3.11-alpine

# Install required packages for Tika
RUN apk add --no-cache openjdk11

# Install Apache Tika
RUN wget -qO- https://repo1.maven.org/maven2/org/apache/tika/tika-server/1.25/tika-server-1.25.jar \
    > /opt/tika-server.jar

# Add the Java to /PATH
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-headless.x86_64

# Set env vars
ENV TIKA_SERVER_JAR "/opt/tika-server.jar"
ENV TIKA_JAVA "/opt/lib/jvm/java-1.8.0-openjdk-1.8.0.252.b09-2.lambda2.0.1.x86_64/jre/bin/java"

# Verify Java installation
RUN java -version

# Verify Tika installation
RUN echo $TIKA_JAVA