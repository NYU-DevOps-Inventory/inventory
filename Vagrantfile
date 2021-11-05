# -*- mode: ruby -*-
# vi: set ft=ruby :
################################################################################
#  - Squad: Inventory
#  - Members:
#      Chen, Peng-Yu | pyc305@nyu.edu | New York | UTC-5
#      Lai, Yu-Wen   | yl8332@nyu.edu | New York | UTC-5
#      Zhang, Haoran | hz2613@nyu.edu | New York | UTC-5
#      Wen, Xuezhou  | xw2447@nyu.edu | New York | UTC-5
#      Hung, Ginkel  | ch3854@nyu.edu | New York | UTC-5
# - Resource URL: /inventory
# - Description:
# The inventory resource keeps track of how many of each product we
# have in our warehouse. At a minimum it should reference a product and the
# quantity on hand. Inventory should also track restock levels and the condition
# of the item (i.e., new, open box, used). Restock levels will help you know
# when to order more products. Being able to query products by their condition
# (e.g., new, used) could be very useful.
################################################################################

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.hostname = "ubuntu"

  # set up network ip and port forwarding
  config.vm.network "forwarded_port", guest: 5000, host: 3000, host_ip: "127.0.0.1"
  config.vm.network "private_network", ip: "192.168.33.10"

  # Windows users need to change the permission of files and directories
  # so that nosetests runs without extra arguments.
  # Mac users can comment this next line out
  config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=775,fmode=664"]

  ##############################################################################
  # Provider for VirtualBox
  ##############################################################################
  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "1024"
    vb.cpus = 2
    # Fixes DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  ##############################################################################
  # Provider for Docker on Intel / ARM (aarch64)
  ##############################################################################
  config.vm.provider :docker do |docker, override|
    override.vm.box = nil
    docker.image = "rofrano/vagrant-provider:debian"
    docker.remains_running = true
    docker.has_ssh = true
    docker.privileged = true
    docker.volumes = ["/sys/fs/cgroup:/sys/fs/cgroup:ro"]
    # Uncomment to force arm64 for testing images on Intel
    # docker.create_args = ["--platform=linux/arm64"]
  end

  ##############################################################################
  # Copy essential configuration files from local machine
  ##############################################################################
  config_paths = [
    "~/.gitconfig", # make your git credentials correct
    "~/.ssh/github", # make your git credentials work
    "~/.vimrc", # make vi/vim look the same
    "~/.bluemix/apiKey.json" # IBM Cloud API Key
  ]

  config_paths.each { |config_path|
    if File.exists?(File.expand_path(config_path))
      config.vm.provision "file", source: config_path, destination: config_path
    end
  }

  ##############################################################################
  # Create a Python 3 virtual environment
  ##############################################################################
  config.vm.provision "shell", inline: <<-SHELL
    # Install Python 3 and related tools
    apt-get upgrade
    apt-get update
    apt-get install -y git python3-pip python3-venv python3-dev python3-selenium
    apt-get install -y build-essential
    apt-get -y autoremove

    # Need PostgreSQL development library to compile on arm64
    apt-get install -y libpq-dev

    # Create a Python 3 virtual environment
    sudo -H -u vagrant sh -c 'python3 -m venv ~/venv'

    # Activate it in ~/.profile
    sudo -H -u vagrant sh -c 'echo ". ~/venv/bin/activate" >> ~/.profile'

    # Install app dependencies in venv as a vagrant uesr
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && pip install -U pip && pip install wheel'
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && cd /vagrant && pip install -r requirements.txt'
  SHELL

  ##############################################################################
  # Add PostgreSQL docker container
  ##############################################################################
  # docker run -d --name postgres -p 5432:5432 -v psql_data:/var/lib/postgresql/data postgres
  config.vm.provision :docker do |d|
    d.pull_images "postgres:alpine"
    d.run "postgres:alpine",
       args: "-d --name postgres -p 5432:5432 -v psql_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres"
  end

  ######################################################################
  # Setup a Bluemix and Kubernetes environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "\n************************************"
    echo " Installing IBM Cloud CLI..."
    echo "************************************\n"
    # Install IBM Cloud CLI as Vagrant user
    sudo -H -u vagrant sh -c '
    curl -fsSL https://clis.cloud.ibm.com/install/linux | sh && \
    ibmcloud cf install && \
    echo "alias ic=ibmcloud" >> ~/.bashrc
    '
    # Show completion instructions
    sudo -H -u vagrant sh -c "echo alias ic=/usr/local/bin/ibmcloud >> ~/.bash_aliases"
    echo "\n************************************"
    echo "If you have an IBM Cloud API key in ~/.bluemix/apiKey.json"
    echo "You can login with the following command:"
    echo "\n"
    echo "ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apikey.json -r us-south"
    echo "ibmcloud target --cf -o <your_org_here> -s dev"
    echo "\n************************************"
  SHELL

end
