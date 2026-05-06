CREATE TABLE facturas(
	id_factura VARCHAR(200) NOT NULL,
	fecha_factura DATE NOT NULL,
	nombre_empresa VARCHAR(200) NOT NULL,
	costo_total NUMERIC(15, 2) NOT NULL,
	url_factura VARCHAR(300) NOT NULL,
	fk_placavehiculo VARCHAR(10) NOT NULL
);

CREATE TABLE servicios(
	id_servicio INT GENERATED ALWAYS AS IDENTITY NOT NULL,
	nombre VARCHAR(150) NOT NULL,
	costo NUMERIC(15, 2) NOT NULL,
	cantidad NUMERIC(10, 2) NOT NULL,
	fk_idfactura VARCHAR(200) NOT NULL
);

CREATE TABLE tarjetapropiedad(
	numero_tarjeta BIGINT NOT NULL,
	nombre_propietario VARCHAR(250) NOT NULL,
	cilindraje INT NOT NULL,
	documento_propietario BIGINT NOT NULL,
	marca VARCHAR(100) NOT NULL,
	clase_vehiculo VARCHAR(100) NOT NULL,
	modelo VARCHAR(100) NOT NULL,
	capacidad INT NOT NULL,
	servicio VARCHAR(100) NOT NULL,
	tipo_carroceria VARCHAR(100) NOT NULL,
	linea_vehiculo VARCHAR(100) NOT NULL,
	numero_motor VARCHAR(150) NOT NULL,
	combustible VARCHAR(80) NOT NULL,
	color VARCHAR(100) NOT NULL,
	placa VARCHAR(10) NOT NULL,
	fk_placavehiculo VARCHAR(10) NOT NULL
);

CREATE TABLE usuario_vehiculo(
	pfk_usuario BIGINT NOT NULL,
	pfk_vehiculo VARCHAR(10) NOT NULL,
	fecha_registro DATE DEFAULT CURRENT_DATE NOT NULL,
	estado VARCHAR(45) NOT NULL,
	kilometros_registro INT
);

CREATE TABLE usuarios(
	documento_identidad BIGINT NOT NULL,
	nombres VARCHAR(100) NOT NULL,
	apellidos VARCHAR(100) NOT NULL,
	correo VARCHAR(150) NOT NULL,
	fecha_nacimiento DATE NOT NULL,
	rol VARCHAR(100) NOT NULL,
	fecha_registro DATE DEFAULT CURRENT_DATE,
	contrasena VARCHAR(280) NOT NULL
);

CREATE TABLE vehiculos(
	placa VARCHAR(10) NOT NULL,
	cilindraje INTEGER NOT NULL,
	marca VARCHAR(100) NOT NULL
);

/*LLAVES PRIMARIAS*/
ALTER TABLE facturas
ADD CONSTRAINT pk_facturas
PRIMARY KEY(id_factura);

ALTER TABLE servicios
ADD CONSTRAINT pk_servicios
PRIMARY KEY(id_servicio);

ALTER TABLE tarjetapropiedad
ADD CONSTRAINT pk_tarjetapropiedad
PRIMARY KEY(numero_tarjeta);

ALTER TABLE usuario_vehiculo
ADD CONSTRAINT pk_usuario_vehiculo
PRIMARY KEY(pfk_usuario, pfk_vehiculo);

ALTER TABLE usuarios
ADD CONSTRAINT pk_usuarios
PRIMARY KEY(documento_identidad);

ALTER TABLE vehiculos
ADD CONSTRAINT pk_vehiculos
PRIMARY KEY(placa);

/*llaves foraneas*/

ALTER TABLE facturas
ADD CONSTRAINT fkvehiculo_factura
FOREIGN KEY (fk_placavehiculo)
REFERENCES vehiculos(placa);

ALTER TABLE servicios
ADD CONSTRAINT fkfactura_servicios
FOREIGN KEY (fk_idfactura)
REFERENCES facturas(id_factura);

ALTER TABLE tarjetapropiedad
ADD CONSTRAINT fkvehiculo_tarjetapropiedad
FOREIGN KEY (fk_placavehiculo)
REFERENCES vehiculos(placa);

ALTER TABLE usuario_vehiculo
ADD CONSTRAINT fkusuario_usuario_vehiculo
FOREIGN KEY (pfk_usuario)
REFERENCES usuarios(documento_identidad);

ALTER TABLE usuario_vehiculo
ADD CONSTRAINT fkvehiculo_usuario_vehiculo
FOREIGN KEY (pfk_vehiculo)
REFERENCES vehiculos(placa);




