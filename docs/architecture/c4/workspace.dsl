workspace "VotoEPIS" "Modelo C4 de la plataforma de elección digital de delegados estudiantiles de la EPIS" {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante votante" "Estudiante de la EPIS que figura en el padrón y vota una sola vez, en secreto."
        comite = person "Comité electoral" "Configura la elección, carga el padrón, publica los resultados y firma el acta."
        auditor = person "Auditor" "Verifica de forma independiente que el conteo coincide con el resultado oficial."

        votoepis = softwareSystem "VotoEPIS" "Permite votar en secreto, contar los votos y auditar la elección de delegados estudiantiles."

        correo = softwareSystem "Servidor de correo institucional" "Entrega los códigos de acceso y los comprobantes a los correos de los estudiantes." "Externo"
        academico = softwareSystem "Sistema académico UNSA" "Origen del padrón; no hay integración directa: el comité entrega el padrón en un archivo CSV." "Externo"

        estudiante -> votoepis "Vota en secreto y consulta su comprobante"
        comite -> votoepis "Configura la elección, carga el padrón y publica resultados y acta"
        auditor -> votoepis "Verifica el conteo de forma independiente"
        votoepis -> correo "Envía códigos de acceso y comprobantes" "SMTP"
        comite -> academico "Obtiene el padrón en un archivo CSV"
    }

    views {
        systemContext votoepis "Contexto" "Nivel 1: VotoEPIS y su entorno." {
            include *
            include academico
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
