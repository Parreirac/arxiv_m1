provider "aws" {
  region = "us-east-1"
}

#values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
# fonctionne pas trop de filtre !
/*data "aws_ami" "neo4j" {
  most_recent = true

  #filter {
  #  name   = "name"
  #  values = ["neo4j*"]
  #}

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["amazon"]
}*/

# Trouve l'AMI la plus récente pour Amazon Linux 2
data "aws_ami" "amazon_linux" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*"]
  }

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

# Définition des variables
variable "private_key_path" {
  description = "Donner le fichier private_key"
}

resource "aws_security_group" "neo4j" {
  name_prefix = "neo4j-sg-"

  ingress {
    from_port   = 7474
    to_port     = 7474
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 7687
    to_port     = 7687
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "neo4j" {
  #ami           = data.aws_ami.neo4j.id
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.neo4j.id]
  #security_groups = [aws_security_group.neo4j.id]
  #key_name               = var.key_name
  key_name = "vockey"
  associate_public_ip_address = true


    connection {
    agent       = false
    type = "ssh"
    user        = "ec2-user"
    private_key = "${file(var.private_key_path)}"
    host =   coalesce(self.public_ip, self.private_ip) #  "${self.private_ip}"
  }


  provisioner "remote-exec" {
    inline = [
    /*  #"sudo apt update -y",
      #"sudo apt install -y gnupg2 curl",
      #"curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -", # fonctionne pas !
      #"echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list",
      #"sudo apt update -y",
      #"sudo apt install -y neo4j",
      #"sudo systemctl enable neo4j",
      #"sudo systemctl start neo4j"
      "sudo apt-get update",   # The apt-get command only works on Debian, Ubuntu, and its derivatives.
      "sudo apt-get install -y apt-transport-https",
      "wget --no-check-certificate --quiet -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -",
      "echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list",
      "sudo apt-get update",
      "sudo apt-get install -y neo4j=4.3.3"
      ]*/
      #user_data = <<-EOF
              #!/bin/bash"
              "wget --no-verbose https://neo4j.com/artifact.php?name=neo4j-community-4.3.5-unix.tar.gz -O neo4j.tar.gz",
              "tar -xzf neo4j.tar.gz",
              "mv neo4j-* neo4j",
              "cd neo4j",
              "./bin/neo4j-admin set-initial-password mypassword",
              "./bin/neo4j start"
      ]
              #EOF

  }
}

output "public_ip" {
  value = aws_instance.neo4j.public_ip
}

output "neo4j_url" {
  value = "http://${aws_instance.neo4j.public_ip}:7474"
}
