# Build this image using "make docker-image" from the root of the project
FROM ubuntu:23.10
ARG GIT_ARCH
SHELL ["/bin/bash", "-c"]

RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|http://mirrors.dotsrc.org/ubuntu/|g' /etc/apt/sources.list

# Install the runtime dependencies
# NOTE: x11-xserver-utils is needed for the using the hosts X server to run libreoffice
ENV TZ=Europe/Oslo
RUN apt-get update && \
    apt-get upgrade -y && \
    DEBIAN_FRONTEND="noninteractive" apt-get install -y \
        curl git vim sudo wget tzdata \
        python3 python3-pip python3-venv

# clean up the apt cache to reduce the image size
RUN rm -rf /var/lib/apt/lists/*

ARG user=docker-user
ARG home=/home/$user

# Add user and set up sudo
RUN useradd --create-home -s /bin/bash $user \
        && echo $user:ubuntu | chpasswd \
        && adduser $user sudo \
        && echo "$user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ARG proj_name=new-python-github-project
ADD ${GIT_ARCH} ${home}/${proj_name}
RUN chown -R $user:$user ${home}/${proj_name}
# Copy over some convenience scripts
# COPY --chown=$user:$user container/* ${home}/${proj_name}
WORKDIR $home/${proj_name}

ENV PATH="${home}/${proj_name}/docker/container:${PATH}"
ENV USER=$user
ENV SHELL=/bin/bash
USER $user

CMD ["/bin/bash"]
