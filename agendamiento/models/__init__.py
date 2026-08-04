from .usuarios import CustomUser, RolUsuario
from .pacientes import Paciente
from .especialistas import Especialidad, Consultorio, Especialista, HorarioLaboral, EstadoTurno
from .citas import Cita, AusenciasPermisos, EstadoCita, EstadoAprobacion, ListaEspera, EstadoListaEspera

__all__ = [
    'CustomUser',
    'RolUsuario',
    'Paciente',
    'Especialidad',
    'Consultorio',
    'Especialista',
    'HorarioLaboral',
    'EstadoTurno',
    'Cita',
    'AusenciasPermisos',
    'EstadoCita',
    'EstadoAprobacion',
    'ListaEspera',
    'EstadoListaEspera',
]
def load_tests(loader, tests, pattern):
    return tests
