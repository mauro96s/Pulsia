/**
 * PulsiaCalendar - Wrapper Orientado a Objetos para FullCalendar.js (Pulsia Medical Systems)
 * Proporciona un sistema de calendario unificado con soporte para roles (Administrador, Recepcionista, Especialista, Paciente).
 */

class PulsiaCalendar {
    constructor(role, containerSelector, options = {}) {
        this.role = role || 'Administrador';
        this.containerSelector = containerSelector;
        this.options = options;
        this.calendar = null;
        this.currentViewMode = 'month'; // 'month' o 'dayDetail'
        this.selectedDateStr = null;
        this.allEvents = [];

        this.init();
    }

    init() {
        const containerEl = document.querySelector(this.containerSelector);
        if (!containerEl) {
            console.error(`PulsiaCalendar: No se encontró el contenedor con el selector '${this.containerSelector}'`);
            return;
        }

        const headerToolbarConfig = {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        };

        const calendarOptions = {
            initialView: 'dayGridMonth',
            locale: 'es',
            firstDay: 1,
            headerToolbar: headerToolbarConfig,
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                day: 'Día'
            },
            slotMinTime: '07:00:00',
            slotMaxTime: '18:00:00',
            events: '/api/citas/eventos/',
            selectable: this.role === 'Administrador' || this.role === 'Recepcionista',
            editable: this.role === 'Administrador' || this.role === 'Recepcionista',

            // Custom Event Content: Cápsulas institucionales con Borde Fuerte + Fondo Suave (Quiet Authority)
            eventContent: (arg) => {
                const props = arg.event.extendedProps || {};
                
                if (props.es_festivo) {
                    return { html: `<div class="p-1 rounded-lg text-center font-extrabold text-[10px] bg-amber-500 text-white truncate border border-amber-600">🇨🇴 Festivo: ${props.nombre_festivo || ''}</div>` };
                }

                const estado = props.estado_cita || 'Programada';
                let hora = '';
                if (arg.event.start) {
                    const d = new Date(arg.event.start);
                    hora = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
                }
                const paciente = props.paciente || arg.event.title;
                const especialista = props.especialista ? `Dr/Dra. ${props.especialista}` : '';

                // Estilo Institucional Unificado: Borde fuerte + Fondo suave
                const stylesMap = {
                    'Programada': 'bg-sky-50 border-2 border-sky-700 text-sky-950',
                    'En_Sala': 'bg-teal-50 border-2 border-teal-700 text-teal-950',
                    'Atendida': 'bg-emerald-50 border-2 border-emerald-700 text-emerald-950',
                    'No_Asistio': 'bg-rose-50 border-2 border-rose-700 text-rose-950',
                    'Pendiente_Reubicacion': 'bg-amber-50 border-2 border-amber-700 text-amber-950',
                    'Cancelada': 'bg-gray-100 border-2 border-gray-600 text-gray-800'
                };
                const styleCls = stylesMap[estado] || 'bg-slate-50 border-2 border-slate-700 text-slate-900';

                return {
                    html: `
                        <div class="w-full h-full ${styleCls} px-2 py-0.5 rounded-lg flex items-center justify-between font-sans text-[11px] leading-none overflow-hidden select-none cursor-pointer shadow-2xs" title="${paciente} ${especialista ? '- ' + especialista : ''} (${hora})">
                            <div class="flex items-center gap-1.5 truncate w-full">
                                <span class="font-extrabold text-[10px] opacity-85 shrink-0">${hora}</span>
                                <span class="opacity-40">|</span>
                                <span class="font-extrabold truncate text-primary">${paciente}</span>
                            </div>
                        </div>
                    `
                };
            },




            // Event Click Handler
            eventClick: (info) => this.handleEventClick(info),

            // Date Click (Abrir vista detalle de día si es Administrador o Recepcionista)
            dateClick: (info) => this.handleDateClick(info),

            // Select Handler
            select: (info) => this.handleDateSelect(info),

            // Event Drop
            eventDrop: (info) => this.handleEventDrop(info),

            // Hook al cargar o actualizar eventos para inyectar contadores por día y festivos
            eventsSet: (events) => {
                this.allEvents = events;
                this.renderHolidayBadges();
                this.renderDailyCountBadges();
                this.renderAllDayHeaderCounts();
                if (this.currentViewMode === 'dayDetail' && this.selectedDateStr) {
                    this.renderTablaCitasDia(this.selectedDateStr);
                    this.renderCarruselSemana(this.selectedDateStr);
                }
            },

            // Hook al cambiar de vista o navegar fechas
            datesSet: () => {
                setTimeout(() => {
                    this.renderHolidayBadges();
                    this.renderDailyCountBadges();
                    this.renderAllDayHeaderCounts();
                }, 50);
            },

            // Renderizado de celdas de días
            dayCellDidMount: (info) => {
                info.el.classList.add('transition-colors', 'duration-200', 'hover:bg-teal-50/50', 'cursor-pointer');
            },

            ...this.options
        };

        this.calendar = new FullCalendar.Calendar(containerEl, calendarOptions);
        this.calendar.render();
    }

    getAllEventsList() {
        if (this.allEvents && this.allEvents.length > 0) {
            return this.allEvents;
        }
        if (this.calendar) {
            return this.calendar.getEvents();
        }
        return [];
    }

    formatDateObjToYMD(dateObj) {
        const y = dateObj.getFullYear();
        const m = String(dateObj.getMonth() + 1).padStart(2, '0');
        const d = String(dateObj.getDate()).padStart(2, '0');
        return `${y}-${m}-${d}`;
    }

    getEventDateStr(evt) {
        if (!evt) return '';
        if (typeof evt.startStr === 'string' && evt.startStr.length >= 10) {
            return evt.startStr.slice(0, 10);
        }
        if (evt.start) {
            const d = new Date(evt.start);
            const y = d.getUTCFullYear();
            const m = String(d.getUTCMonth() + 1).padStart(2, '0');
            const day = String(d.getUTCDate()).padStart(2, '0');
            return `${y}-${m}-${day}`;
        }
        return '';
    }

    getHolidayInfoForDate(dateStr) {
        if (!dateStr) return null;
        const targetDate = dateStr.slice(0, 10);
        const events = this.getAllEventsList();
        for (let i = 0; i < events.length; i++) {
            const evt = events[i];
            const props = evt.extendedProps || {};
            if (props.es_festivo) {
                const dStr = this.getEventDateStr(evt);
                if (dStr === targetDate) {
                    return props.nombre_festivo || 'Día Festivo Nacional';
                }
            }
        }
        return null;
    }

    highlightHolidayCells() {
        const events = this.getAllEventsList();
        events.forEach(evt => {
            const props = evt.extendedProps || {};
            if (props.es_festivo) {
                const dStr = this.getEventDateStr(evt);
                if (dStr) {
                    document.querySelectorAll(`[data-date="${dStr}"]`).forEach(cellEl => {
                        cellEl.style.backgroundColor = '#FFEDD5';
                        cellEl.title = `🇨🇴 Festivo: ${props.nombre_festivo || ''}`;
                    });
                }
            }
        });
    }

    renderHolidayBadges() {
        if (!this.calendar || this.calendar.view.type !== 'dayGridMonth') return;

        document.querySelectorAll('.pulsia-holiday-badge').forEach(el => el.remove());

        document.querySelectorAll('.fc-daygrid-day[data-date]').forEach(cellEl => {
            const dateStr = cellEl.getAttribute('data-date');
            if (!dateStr) return;

            const festivoNom = this.getHolidayInfoForDate(dateStr);
            const dayFrameEl = cellEl.querySelector('.fc-daygrid-day-frame') || cellEl;
            const dayTopEl = cellEl.querySelector('.fc-daygrid-day-top');

            if (festivoNom) {
                cellEl.style.backgroundColor = '#FFEDD5';
                cellEl.classList.remove('cursor-pointer');
                cellEl.classList.add('cursor-not-allowed');

                const badge = document.createElement('div');
                badge.className = 'pulsia-holiday-badge mt-1 mb-0.5 mx-auto px-2 py-0.5 rounded-lg text-[10px] font-extrabold bg-amber-500 text-white shadow-2xs flex items-center justify-center gap-1 text-center border border-amber-600 max-w-[95%] truncate';
                badge.title = `🇨🇴 Festivo: ${festivoNom}`;
                badge.innerHTML = `
                    <span class="material-symbols-outlined text-[11px]">flag</span>
                    <span class="truncate">🇨🇴 Festivo: ${festivoNom}</span>
                `;

                if (dayTopEl && dayTopEl.parentNode === dayFrameEl) {
                    dayTopEl.insertAdjacentElement('afterend', badge);
                } else {
                    dayFrameEl.appendChild(badge);
                }
            }
        });
    }

    renderAllDayHeaderCounts() {
        this.highlightHolidayCells();

        const countsByDate = {};
        const events = this.getAllEventsList();
        events.forEach(evt => {
            const props = evt.extendedProps || {};
            if (props.es_festivo) return;
            const dateStr = this.getEventDateStr(evt);
            if (dateStr) {
                countsByDate[dateStr] = (countsByDate[dateStr] || 0) + 1;
            }
        });

        const allDayCells = document.querySelectorAll('.fc-timegrid-all-day .fc-daygrid-day, .fc-timegrid-header .fc-daygrid-day[data-date], .fc-timegrid .fc-daygrid-day[data-date]');
        allDayCells.forEach(cellEl => {
            const dateStr = cellEl.getAttribute('data-date');
            if (dateStr) {
                const festivoNom = this.getHolidayInfoForDate(dateStr);
                const dayFrameEl = cellEl.querySelector('.fc-daygrid-day-frame') || cellEl;
                
                if (festivoNom) {
                    cellEl.style.backgroundColor = '#FFEDD5';
                    dayFrameEl.innerHTML = `
                        <div class="p-1 mx-0.5 my-0.5 rounded-lg text-center font-extrabold text-[11px] bg-amber-500 text-white shadow-2xs border border-amber-600 flex items-center justify-center gap-1" title="Festivo: ${festivoNom}">
                            <span class="material-symbols-outlined text-xs">flag</span>
                            <span class="truncate">🇨🇴 Festivo: ${festivoNom}</span>
                        </div>
                    `;
                } else {
                    const count = countsByDate[dateStr] || 0;
                    dayFrameEl.innerHTML = `
                        <div class="p-1 mx-0.5 my-0.5 rounded-lg text-center font-bold text-[11px] ${count > 0 ? 'bg-teal-100 text-teal-900 border border-teal-300' : 'bg-gray-100 text-gray-500'} flex items-center justify-center gap-1">
                            <span class="material-symbols-outlined text-xs">${count > 0 ? 'event_available' : 'event'}</span>
                            <span>${count} Cita${count !== 1 ? 's' : ''}</span>
                        </div>
                    `;
                }
            }
        });
    }

    renderDailyCountBadges() {
        if (!this.calendar || this.calendar.view.type !== 'dayGridMonth') return;
        this.renderHolidayBadges();

        if (this.role === 'Recepcionista') return; // NO renderizar badge de conteo de citas para recepcionista

        document.querySelectorAll('.pulsia-day-count-badge').forEach(el => el.remove());

        const countsByDate = {};
        const events = this.getAllEventsList();
        events.forEach(evt => {
            const props = evt.extendedProps || {};
            if (props.es_festivo) return;

            const dateStr = this.getEventDateStr(evt);
            if (dateStr) {
                countsByDate[dateStr] = (countsByDate[dateStr] || 0) + 1;
            }
        });

        document.querySelectorAll('.fc-daygrid-day[data-date]').forEach(cellEl => {
            const dateStr = cellEl.getAttribute('data-date');
            if (!dateStr) return;

            const festivoNom = this.getHolidayInfoForDate(dateStr);
            const dayFrameEl = cellEl.querySelector('.fc-daygrid-day-frame') || cellEl;
            const dayTopEl = cellEl.querySelector('.fc-daygrid-day-top');

            if (!festivoNom) {
                const count = countsByDate[dateStr] || 0;
                if (count > 0) {
                    const badge = document.createElement('div');
                    badge.className = 'pulsia-day-count-badge mb-1 mx-auto px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-teal-600 text-white shadow-xs flex items-center justify-center gap-1 transition-all transform hover:scale-105 hover:bg-teal-700 cursor-pointer text-center';
                    badge.title = `Haz clic para ver las ${count} citas de este día`;
                    badge.innerHTML = `
                        <span class="material-symbols-outlined text-[11px]">calendar_month</span>
                        <span>${count} cita${count > 1 ? 's' : ''}</span>
                    `;
                    
                    badge.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.seleccionarDia(dateStr);
                    });

                    if (dayTopEl && dayTopEl.parentNode === dayFrameEl) {
                        dayTopEl.insertAdjacentElement('afterend', badge);
                    } else {
                        dayFrameEl.appendChild(badge);
                    }
                }
            }
        });
    }

    handleDateClick(info) {
        if (!info || !info.dateStr) return;
        if (this.getHolidayInfoForDate(info.dateStr)) return;

        if (this.role === 'Administrador' || this.role === 'Recepcionista') {
            this.seleccionarDia(info.dateStr);
        }
    }

    seleccionarDia(dateStr) {
        this.selectedDateStr = dateStr;
        this.currentViewMode = 'dayDetail';

        const monthWrapper = document.getElementById('calendario-mes-wrapper');
        const detailWrapper = document.getElementById('calendario-detalle-wrapper');
        const btnVolverWrapper = document.getElementById('wrapper-btn-volver-mes');

        if (!monthWrapper || !detailWrapper) return;

        monthWrapper.classList.add('hidden');
        detailWrapper.classList.remove('hidden');

        if (btnVolverWrapper) {
            btnVolverWrapper.classList.remove('hidden');
        }

        this.renderCarruselSemana(dateStr);
        this.renderTablaCitasDia(dateStr);

        detailWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    volverAMes() {
        this.currentViewMode = 'month';

        const monthWrapper = document.getElementById('calendario-mes-wrapper');
        const detailWrapper = document.getElementById('calendario-detalle-wrapper');
        const btnVolverWrapper = document.getElementById('wrapper-btn-volver-mes');

        if (detailWrapper) detailWrapper.classList.add('hidden');
        if (monthWrapper) monthWrapper.classList.remove('hidden');
        if (btnVolverWrapper) btnVolverWrapper.classList.add('hidden');

        if (this.calendar) {
            setTimeout(() => {
                this.calendar.updateSize();
                this.renderHolidayBadges();
                this.renderDailyCountBadges();
            }, 100);
        }
    }

    renderCarruselSemana(targetDateStr) {
        const carruselContainer = document.getElementById('carrusel-semanal-container');
        const tituloFechaEl = document.getElementById('titulo-fecha-seleccionada');
        const labelMesEl = document.getElementById('label-mes-actual-carrusel');
        if (!carruselContainer) return;

        const parts = targetDateStr.split('-');
        const targetDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));

        if (tituloFechaEl) {
            const opciones = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
            const fechaFormateada = targetDate.toLocaleDateString('es-ES', opciones);
            const textoCapital = fechaFormateada.charAt(0).toUpperCase() + fechaFormateada.slice(1);
            const nombreFestivoDia = this.getHolidayInfoForDate(targetDateStr);

            if (nombreFestivoDia) {
                tituloFechaEl.innerHTML = `
                    <span class="flex flex-wrap items-center gap-2">
                        <span>${textoCapital}</span>
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-amber-100 text-amber-900 border border-amber-300">
                            🇨🇴 Festivo: ${nombreFestivoDia}
                        </span>
                    </span>
                `;
            } else {
                tituloFechaEl.textContent = textoCapital;
            }
        }

        if (labelMesEl) {
            const mesFormateado = targetDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
            labelMesEl.textContent = mesFormateado.charAt(0).toUpperCase() + mesFormateado.slice(1);
        }

        const dayOfWeek = targetDate.getDay();
        const diffToMonday = (dayOfWeek === 0 ? -6 : 1 - dayOfWeek);
        const monday = new Date(targetDate);
        monday.setDate(targetDate.getDate() + diffToMonday);

        const espFilter = document.getElementById('filtro-especialidad')?.value || document.getElementById('selectFiltroEspecialidad')?.value || '';
        const medFilter = document.getElementById('filtro-especialista')?.value || document.getElementById('selectFiltroEspecialista')?.value || '';
        const pacFilter = document.getElementById('selectFiltroPaciente')?.value || '';

        const countsByDate = {};
        const events = this.getAllEventsList();
        events.forEach(evt => {
            const props = evt.extendedProps || {};
            if (props.es_festivo) return;

            if (espFilter && String(props.especialidad_id) !== String(espFilter)) return;
            if (medFilter && String(props.especialista_id) !== String(medFilter)) return;
            if (pacFilter && String(props.paciente_id || '') !== String(pacFilter)) return;

            const dStr = this.getEventDateStr(evt);
            if (dStr) {
                countsByDate[dStr] = (countsByDate[dStr] || 0) + 1;
            }
        });

        const diasNombres = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
        let html = '<div class="grid grid-cols-7 gap-1.5 sm:gap-2 w-full text-center">';

        for (let i = 0; i < 7; i++) {
            const currDate = new Date(monday);
            currDate.setDate(monday.getDate() + i);
            const currStr = this.formatDateObjToYMD(currDate);

            const diaNombre = diasNombres[currDate.getDay()];
            const diaNum = currDate.getDate();
            const count = countsByDate[currStr] || 0;
            const isSelected = (currStr === targetDateStr);
            const festivoNom = this.getHolidayInfoForDate(currStr);

            html += `
                <button type="button" onclick="window.pulsiaCal.seleccionarDia('${currStr}')" 
                        class="w-full p-2 sm:p-3 rounded-2xl border transition-all duration-150 flex flex-col items-center justify-center gap-1 shadow-2xs cursor-pointer text-center
                        ${isSelected 
                            ? 'bg-clinical-teal text-white border-clinical-teal shadow-md ring-2 ring-teal-300/40 font-bold' 
                            : (festivoNom ? 'bg-amber-50/70 hover:bg-amber-100/80 border-amber-300 text-amber-900' : 'bg-white hover:bg-teal-50/60 border-gray-200 text-gray-700 hover:border-teal-300')
                        }">
                    <span class="text-[10px] sm:text-xs font-extrabold uppercase tracking-wider ${isSelected ? 'text-teal-100' : (festivoNom ? 'text-amber-800' : 'text-gray-400')}">${diaNombre}</span>
                    <span class="text-lg sm:text-xl font-extrabold ${isSelected ? 'text-white' : (festivoNom ? 'text-amber-950' : 'text-primary')}">${diaNum}</span>
                    ${festivoNom ? `
                        <span class="px-1.5 py-0.5 rounded-full text-[9px] font-extrabold bg-amber-500 text-white shadow-2xs border border-amber-600 truncate max-w-full" title="Festivo: ${festivoNom}">
                            🇨🇴 Festivo
                        </span>
                    ` : `
                        <span class="px-1.5 py-0.5 rounded-full text-[9px] sm:text-[10px] font-bold ${
                            isSelected 
                                ? 'bg-white/20 text-white border border-white/30' 
                                : (count > 0 ? 'bg-teal-100 text-teal-800 border border-teal-200/50' : 'bg-gray-100 text-gray-400')
                        }">
                            ${count} cita${count !== 1 ? 's' : ''}
                        </span>
                    `}
                </button>
            `;
        }
        html += '</div>';

        carruselContainer.innerHTML = html;
    }

    renderTablaCitasDia(targetDateStr) {
        const tbody = document.getElementById('tbody-citas-dia');
        const contadorCitasEl = document.getElementById('contador-tabla-citas');
        const bannerFestivoEl = document.getElementById('contenedor-banner-festivo');
        if (!tbody) return;

        const nombreFestivoDia = this.getHolidayInfoForDate(targetDateStr);
        if (bannerFestivoEl) {
            if (nombreFestivoDia) {
                bannerFestivoEl.innerHTML = `
                    <div class="p-4 rounded-2xl bg-gradient-to-r from-amber-50 via-orange-50 to-amber-100 border border-amber-300/80 shadow-xs flex items-center gap-3.5 animate-fade-in-up">
                        <div class="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center font-bold shrink-0 shadow-xs">
                            <span class="material-symbols-outlined text-2xl">flag</span>
                        </div>
                        <div>
                            <h4 class="font-heading font-extrabold text-sm text-amber-950 flex items-center gap-2">
                                <span>🇨🇴 Día Festivo Oficial en Colombia:</span>
                                <span class="underline decoration-amber-500">${nombreFestivoDia}</span>
                            </h4>
                            <p class="text-xs text-amber-900/80 mt-0.5">
                                Esta fecha está marcada como festivo oficial por calendario (Ley Emiliani). No se programan jornadas laborales de consulta ordinaria.
                            </p>
                        </div>
                    </div>
                `;
                bannerFestivoEl.classList.remove('hidden');
            } else {
                bannerFestivoEl.innerHTML = '';
                bannerFestivoEl.classList.add('hidden');
            }
        }

        const espFilter = document.getElementById('filtro-especialidad')?.value || document.getElementById('selectFiltroEspecialidad')?.value || '';
        const medFilter = document.getElementById('filtro-especialista')?.value || document.getElementById('selectFiltroEspecialista')?.value || '';
        const pacFilter = document.getElementById('selectFiltroPaciente')?.value || '';

        const citasDia = this.getAllEventsList().filter(evt => {
            const props = evt.extendedProps || {};
            if (props.es_festivo) return false;

            const dStr = this.getEventDateStr(evt);
            if (dStr !== targetDateStr) return false;

            if (espFilter && String(props.especialidad_id) !== String(espFilter)) return false;
            if (medFilter && String(props.especialista_id) !== String(medFilter)) return false;
            if (pacFilter && String(props.paciente_id || '') !== String(pacFilter)) return false;

            return true;
        });

        if (contadorCitasEl) {
            contadorCitasEl.textContent = `${citasDia.length} Citas Registradas`;
        }

        if (citasDia.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-10 animate-fade-in-up">
                        <div class="flex flex-col items-center justify-center gap-2">
                            <span class="material-symbols-outlined text-4xl text-gray-300">event_busy</span>
                            <p class="text-sm font-bold text-gray-500">No hay citas programadas para este día con los filtros seleccionados.</p>
                            <p class="text-xs text-gray-400">Puedes ajustar los filtros superiores o seleccionar otro día en el carrusel.</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        citasDia.sort((a, b) => new Date(a.start) - new Date(b.start));

        const colorsState = {
            'Programada': 'bg-slate-700 text-white',
            'En_Sala': 'bg-teal-700 text-white',
            'Atendida': 'bg-emerald-600 text-white',
            'Cancelada': 'bg-gray-500 text-white',
            'No_Asistio': 'bg-rose-700 text-white',
            'Pendiente_Reubicacion': 'bg-amber-600 text-white'
        };

        let rowsHtml = '';
        citasDia.forEach((evt, idx) => {
            const props = evt.extendedProps || {};
            const startObj = new Date(evt.start);
            const horaInicio = startObj.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', hour12: true });

            const estado = props.estado_cita || 'Programada';
            const badgeClass = colorsState[estado] || 'bg-primary text-white';
            const animDelay = (idx * 0.04).toFixed(2);

            rowsHtml += `
                <tr class="animate-fade-in-up hover:bg-teal-50/40 transition-colors border-b border-gray-100" style="animation-delay: ${animDelay}s">
                    <td class="px-4 py-3 font-bold text-primary whitespace-nowrap">
                        <div class="flex items-center gap-1.5">
                            <span class="material-symbols-outlined text-teal-600 text-base">schedule</span>
                            <span>${horaInicio}</span>
                        </div>
                    </td>
                    <td class="px-4 py-3 font-semibold text-gray-800">
                        ${props.paciente || 'Paciente N/A'}
                    </td>
                    <td class="px-4 py-3 text-gray-700 font-medium">
                        ${props.especialista || 'Médico N/A'}
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap">
                        <span class="px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">
                            ${props.consultorio || 'N/A'}
                        </span>
                    </td>
                    <td class="px-4 py-3 whitespace-nowrap">
                        <span class="px-3 py-1 rounded-full text-[11px] font-bold ${badgeClass}">
                            ${estado.replace('_', ' ')}
                        </span>
                    </td>
                    <td class="px-4 py-3 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1.5">
                            <!-- Botón Ver Detalle -->
                            <button type="button" 
                                    title="Ver Detalle"
                                    onclick="window.abrirModalDetalleCita({
                                        id: '${evt.id}',
                                        titulo: '${(evt.title || '').replace(/'/g, "\\'")}',
                                        inicio: '${evt.startStr}',
                                        fin: '${evt.endStr || ''}',
                                        paciente: '${(props.paciente || '').replace(/'/g, "\\'")}',
                                        especialista: '${(props.especialista || '').replace(/'/g, "\\'")}',
                                        consultorio: '${(props.consultorio || '').replace(/'/g, "\\'")}',
                                        estado: '${props.estado_cita}',
                                        notas: '${(props.notas_clinicas || '').replace(/'/g, "\\'")}'
                                    })"
                                    class="inline-flex items-center justify-center w-8 h-8 rounded-xl bg-teal-50 hover:bg-teal-600 text-teal-700 hover:text-white transition shadow-2xs cursor-pointer">
                                <span class="material-symbols-outlined text-base">visibility</span>
                            </button>

                            <!-- Botón Reagendar Cita (Recepcionista / Admin) -->
                            ${(this.role === 'Recepcionista' || this.role === 'Administrador') && (estado === 'Programada' || estado === 'Pendiente_Reubicacion') ? `
                                <a href="/recepcion/agendar-cita/?cita_id=${evt.id}&modo=reprogramar" 
                                   title="Reagendar Cita" 
                                   class="inline-flex items-center justify-center w-8 h-8 rounded-xl bg-amber-50 hover:bg-amber-600 text-amber-700 hover:text-white transition shadow-2xs cursor-pointer">
                                    <span class="material-symbols-outlined text-base">event_repeat</span>
                                </a>
                            ` : ''}
                        </div>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = rowsHtml;
    }

    handleEventClick(info) {
        const props = info.event.extendedProps;
        if (typeof window.abrirModalDetalleCita === 'function') {
            window.abrirModalDetalleCita({
                id: info.event.id,
                titulo: info.event.title,
                inicio: info.event.start,
                fin: info.event.end,
                paciente: props.paciente,
                especialista: props.especialista,
                consultorio: props.consultorio,
                estado: props.estado_cita,
                notas: props.notas_clinicas
            });
        }
    }

    handleDateSelect(info) {
        if (this.role === 'Administrador' || this.role === 'Recepcionista') {
            if (typeof window.abrirModalNuevaCita === 'function') {
                window.abrirModalNuevaCita(info.startStr, info.endStr);
            }
        }
    }

    handleEventDrop(info) {
        if (this.role !== 'Administrador' && this.role !== 'Recepcionista') {
            info.revert();
            return;
        }

        if (!confirm(`¿Deseas mover la cita a la nueva fecha: ${info.event.start.toLocaleString()}?`)) {
            info.revert();
            return;
        }

        fetch('/api/citas/actualizar_fecha/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                cita_id: info.event.id,
                nueva_fecha_inicio: info.event.start.toISOString(),
                nueva_fecha_fin: info.event.end ? info.event.end.toISOString() : info.event.start.toISOString()
            })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert(data.error || 'Error al actualizar la cita.');
                info.revert();
            } else {
                console.log("Cita actualizada exitosamente");
            }
        })
        .catch(err => {
            console.error("Error en petición:", err);
            info.revert();
        });
    }

    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    refetchEvents() {
        if (this.calendar) {
            this.calendar.refetchEvents();
        }
    }
}

// Exportar globalmente
window.PulsiaCalendar = PulsiaCalendar;
