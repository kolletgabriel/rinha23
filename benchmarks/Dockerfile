FROM eclipse-temurin:20-jdk

WORKDIR /opt

# Installing Gatling and removing example/tutorial files:
ARG URL="https://repo1.maven.org/maven2/io/gatling/highcharts/gatling-charts-highcharts-bundle/3.9.5/gatling-charts-highcharts-bundle-3.9.5-bundle.zip"
RUN apt update && apt install unzip \
    && curl -fsSL "$URL" > /tmp/gatling.zip \
    && unzip -d . /tmp/gatling.zip \
    && mv gatling-charts-highcharts-bundle-3.9.5 gatling \
    && rm /tmp/gatling.zip \
    && rm -rf gatling/user-files/resources/* \
    && rm -rf gatling/user-files/simulations/*

# Using files from the challenge:
COPY ./user-files/resources ./gatling/user-files/resources
COPY ./user-files/simulations ./gatling/user-files/simulations

ENTRYPOINT ["gatling/bin/gatling.sh"]
CMD ["-rm", "local", "-s", "RinhaBackendSimulation", "-rd", "rinha23-benchmark"]
