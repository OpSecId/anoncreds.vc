FROM ghcr.io/openwallet-foundation/acapy-agent:py3.12-1.5.1

USER root

RUN pip install --no-cache-dir \
    "git+https://github.com/openwallet-foundation/acapy-plugins@1.5.1#subdirectory=webvh" \
    "git+https://github.com/openwallet-foundation/acapy-plugins@1.5.1#subdirectory=status_list" \
    "git+https://github.com/openwallet-foundation/acapy-plugins@1.5.1#subdirectory=connection_update"

USER $user
COPY ./configs.yml configs.yml

CMD ["start", "--arg-file", "configs.yml"]
