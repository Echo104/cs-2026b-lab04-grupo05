workspace "VotoEPIS" "Modelo C4 de la plataforma de elección digital de delegados estudiantiles de la EPIS" {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante votante" "Estudiante de la EPIS que figura en el padrón y vota una sola vez, en secreto."
        comite = person "Comité electoral" "Configura la elección, carga el padrón, publica los resultados y firma el acta."
        auditor = person "Auditor" "Verifica de forma independiente que el conteo coincide con el resultado oficial."

        votoepis = softwareSystem "VotoEPIS" "Permite votar en secreto, contar los votos y auditar la elección de delegados estudiantiles." {
            web = container "Web de votación" "Interfaz para votar, administrar la elección y consultar resultados." "Aplicación web responsive (navegador)" "Web Browser"
            api = container "API VotoEPIS" "Monolito modular que implementa los casos de uso mediante una API REST." "Python / Django"
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
