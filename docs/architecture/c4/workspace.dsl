workspace "VotoEPIS" "Modelo C4 de la plataforma de elección digital de delegados estudiantiles de la EPIS" {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante votante" "Estudiante de la EPIS que figura en el padrón y vota una sola vez, en secreto."
        comite = person "Comité electoral" "Configura la elección, carga el padrón, publica los resultados y firma el acta."
        auditor = person "Auditor" "Verifica de forma independiente que el conteo coincide con el resultado oficial."

        votoepis = softwareSystem "VotoEPIS" "Permite votar en secreto, contar los votos y auditar la elección de delegados estudiantiles." {
            web = container "Web de votación" "Interfaz para votar, administrar la elección y consultar resultados." "Aplicación web responsive (navegador)" "Web Browser"
            api = container "API VotoEPIS" "Monolito modular que implementa los casos de uso mediante una API REST." "Python / Django" {
                elecciones = component "Módulo Elección y padrón" "Configura la elección y sus listas, carga el padrón y controla el estado de la elección." "Django app"
                autenticacion = component "Módulo Autenticación" "Verifica el correo en el padrón y valida el código de un solo uso." "Django app"
                votacion = component "Módulo Votación" "Registra el voto anónimo y la participación, y emite el comprobante." "Django app"
                resultados = component "Módulo Resultados" "Cuenta los votos y genera el acta de la elección." "Django app"
                auditoria = component "Módulo Auditoría" "Exporta la urna anonimizada con su huella para el recuento independiente." "Django app"
            }
            padron = container "Base de datos del padrón" "Padrón, elecciones, listas y participaciones: quién votó, nunca por quién." "PostgreSQL (esquema padron)" "Database"
            urna = container "Base de datos de la urna" "Votos anónimos: sin identidad del estudiante y sin marca de tiempo." "PostgreSQL (esquema urna)" "Database"
            monitoreo = container "Monitoreo" "Muestra métricas y estado de salud del servicio." "Grafana"
        }

        correo = softwareSystem "Servidor de correo institucional" "Entrega los códigos de acceso y los comprobantes a los correos de los estudiantes." "Externo"
        academico = softwareSystem "Sistema académico UNSA" "Origen del padrón; no hay integración directa: el comité entrega el padrón en un archivo CSV." "Externo"

        estudiante -> votoepis "Vota en secreto y consulta su comprobante"
        comite -> votoepis "Configura la elección, carga el padrón y publica resultados y acta"
        auditor -> votoepis "Verifica el conteo de forma independiente"
        votoepis -> correo "Envía códigos de acceso y comprobantes" "SMTP"
        comite -> academico "Obtiene el padrón en un archivo CSV"

        estudiante -> votoepis.web "Usa" "HTTPS"
        comite -> votoepis.web "Usa" "HTTPS"
        auditor -> votoepis.web "Usa" "HTTPS"
        votoepis.web -> votoepis.api "Llama a" "HTTPS/JSON (REST)"
        votoepis.api -> votoepis.padron "Lee y escribe el padrón y las participaciones" "SQL/TCP"
        votoepis.api -> votoepis.urna "Escribe los votos y los lee para el conteo y la auditoría" "SQL/TCP"
        votoepis.api -> correo "Envía códigos de acceso y comprobantes" "SMTP"
        votoepis.api -> votoepis.monitoreo "Envía métricas de salud" "HTTP"

        votoepis.web -> votoepis.api.autenticacion "Solicita y valida el código de acceso" "HTTPS/JSON"
        votoepis.web -> votoepis.api.votacion "Emite el voto" "HTTPS/JSON"
        votoepis.web -> votoepis.api.elecciones "Configura la elección y carga el padrón" "HTTPS/JSON"
        votoepis.web -> votoepis.api.resultados "Consulta resultados y acta" "HTTPS/JSON"
        votoepis.web -> votoepis.api.auditoria "Descarga la urna anonimizada y su huella" "HTTPS/JSON"
        votoepis.api.autenticacion -> votoepis.api.elecciones "Consulta si el correo está en el padrón"
        votoepis.api.votacion -> votoepis.api.elecciones "Verifica que la elección esté abierta"
        votoepis.api.votacion -> votoepis.api.autenticacion "Obtiene el estudiante de la sesión"
        votoepis.api.resultados -> votoepis.api.votacion "Lee la urna (solo lectura)"
        votoepis.api.resultados -> votoepis.api.elecciones "Marca la elección como escrutada y publicada"
        votoepis.api.auditoria -> votoepis.api.resultados "Consulta el acta y su huella"
        votoepis.api.auditoria -> votoepis.api.votacion "Exporta la urna anonimizada (solo lectura)"
        votoepis.api.elecciones -> votoepis.padron "Lee y escribe elecciones, listas y padrón" "SQL/TCP"
        votoepis.api.autenticacion -> votoepis.padron "Verifica el correo en el padrón" "SQL/TCP"
        votoepis.api.autenticacion -> correo "Envía el código de acceso" "SMTP"
        votoepis.api.votacion -> votoepis.padron "Registra la participación" "SQL/TCP"
        votoepis.api.votacion -> votoepis.urna "Registra el voto anónimo en la misma transacción" "SQL/TCP"
        votoepis.api.votacion -> correo "Envía el comprobante de participación" "SMTP"
        votoepis.api.resultados -> votoepis.urna "Cuenta los votos por lista" "SQL/TCP"
        votoepis.api.auditoria -> votoepis.urna "Exporta la urna anonimizada" "SQL/TCP"
    }

    views {
        systemContext votoepis "Contexto" "Nivel 1: VotoEPIS y su entorno." {
            include *
            include academico
            autolayout lr
        }
        container votoepis "Contenedores" "Nivel 2: contenedores de VotoEPIS." {
            include *
            autolayout lr
        }
        component votoepis.api "Componentes" "Nivel 3: módulos de la API." {
            include *
            autolayout lr
        }
        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}
