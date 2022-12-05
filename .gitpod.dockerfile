FROM gitpod/workspace-full

USER gitpod

RUN bash -c ". /home/gitpod/.sdkman/bin/sdkman-init.sh && \
    sdk install java 17.0.3-ms && \
    sdk default java 17.0.3-ms && \
    sdk install gradle 7.5.1 && \
    sdk default gradle 7.5.1 && \
    sdk install kotlin 1.7.21 && \
    sdk default kotlin 1.7.21"
