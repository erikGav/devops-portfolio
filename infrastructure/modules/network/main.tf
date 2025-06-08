resource "aws_vpc" "vpc" {
  cidr_block = var.vpc_config.cidr_block

  tags = {
    Name = "${var.naming_prefix}-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = "${var.naming_prefix}-igw"
  }
}


resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_subnet.id

  tags = {
    Name = "${var.naming_prefix}-nat-gateway-1"
  }

  depends_on = [aws_internet_gateway.igw]
}

resource "aws_eip" "nat" {
  tags = {
    Name = "${var.naming_prefix}-nat-eip-1"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = var.vpc_config.public_subnet
  availability_zone       = var.vpc_config.availability_zones[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.naming_prefix}-public-subnet-1"
  }
}

resource "aws_subnet" "private_subnets" {
  for_each = { for idx, subnet in var.vpc_config.private_subnets : idx => subnet }

  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = each.value
  availability_zone       = var.vpc_config.availability_zones[each.key % length(var.vpc_config.availability_zones)]
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.naming_prefix}-private-subnet-${each.key}"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.naming_prefix}-route-table"
  }
}

resource "aws_route_table" "private_route_table" {
  for_each = aws_subnet.private_subnets

  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "${var.naming_prefix}-private-route-table-${each.key}"
  }
}

resource "aws_route_table_association" "public_subnets_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table_association" "private_subnets_association" {
  for_each       = aws_subnet.private_subnets
  subnet_id      = each.value.id
  route_table_id = aws_route_table.private_route_table[each.key].id
}

