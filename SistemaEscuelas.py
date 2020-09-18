# -*- coding: utf-8 -*-
import csv
import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Time, Sequence
from sqlalchemy.orm import sessionmaker

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import exists

Base = declarative_base()

class Curso(Base):
    __tablename__ = 'curso'

    id = Column(Integer, Sequence('curso_id_seq'), primary_key=True)
    nombre = Column(String)

    alumnoren = relationship('Alumno', order_by='Alumno.id', back_populates='curso')
    curso_horarios = relationship('Horario', order_by='Horario.hora_desde', back_populates='curso')

    def __repr__(self):
        return "{} {}".format(self.nombre)

class Alumno(Base):
    __tablename__ = 'alumno'

    id = Column(Integer, Sequence('alumno_id_seq'), primary_key=True)
    nombre = Column(String)
    apellido = Column(String)
    curso_id = Column(Integer, ForeignKey('curso.id'))

    curso = relationship('Curso', back_populates='alumnoren')

    def __repr__(self):
        return "{} {}".format(self.nombre, self.apellido)


class Profesor(Base):
    __tablename__ = 'profesor'

    id = Column(Integer, Sequence('profesor_id_seq'), primary_key=True)
    nombre = Column(String)
    apellido = Column(String)

    profesor_horarios = relationship('Horario', order_by='Horario.hora_desde', back_populates='profesor')

    def __repr__(self):
        return "{} {}".format(self.nombre, self.apellido)


class Horario(Base):
    __tablename__ = 'horario'
    
    id = Column(Integer, Sequence('horario_id_seq'), primary_key=True)
    dia = Column(Integer)
    hora_desde = Column(Time)
    hora_hasta = Column(Time)
    curso_id = Column(Integer, ForeignKey('curso.id'))
    profesor_id = Column(Integer, ForeignKey('profesor.id'))

    curso = relationship('Curso', back_populates='curso_horarios')
    profesor = relationship('Profesor', back_populates='profesor_horarios')

    def __repr__(self):
        return "{} {}".format(self.nombre)


class CursoReport(object):

    def __init__(self, path):
        self.path = path

    def export(self, curso):
        alumnoren = curso.alumnoren
        with open(self.path, 'w') as a_file:
            writer = csv.writer(a_file)
            for alumno in alumnoren:
                writer.writerow([str(alumno)])


class CursoHorarioReport(object):

    def __init__(self, path):
        self.path = path

    def export(self, curso):
        horarios = curso.curso_horarios
        with open(self.path, 'w') as a_file:
            writer = csv.writer(a_file)
            for horario in horarios:
                writer.writerow([horario.dia, horario.hora_desde, horario.hora_hasta, horario.profesor])


class ProfesorHorarioReport(object):
    
    def __init__(self, path):
        self.path = path

    def export(self, profesor):
        horarios = profesor.profesor_horarios
        with open(self.path, 'w') as a_file:
            writer = csv.writer(a_file)
            for horario in horarios:
                writer.writerow([horario.dia, horario.hora_desde, horario.hora_hasta, horario.curso.nombre])


def main(*args, **kwargs):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    curso1 = Curso(nombre='Python')
    curso2 = Curso(nombre='C')
    curso3 = Curso(nombre='Java')

    alumno1 = Alumno(nombre='Juan', apellido='Perez', curso=curso1)
    alumno2 = Alumno(nombre='Elber', apellido='Galarga', curso=curso2)
    alumno3 = Alumno(nombre='Alan', apellido='Brito', curso=curso2)
    alumno4 = Alumno(nombre='John', apellido='Doe', curso=curso3)

    profesor1 = Profesor(nombre='Agustin', apellido='Olmedo')
    profesor2 = Profesor(nombre='Soyla', apellido='Cueva')

    hora1 = datetime.time(16, 0, 0)
    hora2 = datetime.time(18, 0, 0)
    hora3 = datetime.time(20, 0, 0)
    hora4 = datetime.time(22, 0, 0)

    horario1 = Horario(dia=1, hora_desde=hora1, hora_hasta=hora2, curso=curso1, profesor=profesor1)
    horario2 = Horario(dia=2, hora_desde=hora2, hora_hasta=hora3, curso=curso2, profesor=profesor1)
    horario3 = Horario(dia=1, hora_desde=hora1, hora_hasta=hora3, curso=curso3, profesor=profesor2)
    horario4 = Horario(dia=4, hora_desde=hora3, hora_hasta=hora4, curso=curso1, profesor=profesor2)

    session.add(alumno1)
    session.add(alumno2)
    session.add(alumno3)
    session.add(alumno4)

    session.add(profesor1)
    session.add(profesor2)

    session.add(horario1)
    session.add(horario2)
    session.add(horario3)
    session.add(horario4)

    session.commit()

    CursoReport('curso_{}.csv'.format(curso1.nombre)).export(curso1)
    CursoReport('curso_{}.csv'.format(curso2.nombre)).export(curso2)

    CursoHorarioReport('curso_horario_{}.csv'.format(curso1.nombre)).export(curso1)
    CursoHorarioReport('curso_horario_{}.csv'.format(curso2.nombre)).export(curso2)

    ProfesorHorarioReport('profesor_horario_{}.csv'.format(profesor1)).export(profesor1)


if __name__ == "__main__":
    main()
