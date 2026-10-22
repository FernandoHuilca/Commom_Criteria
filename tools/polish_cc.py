"""Revisión editorial del catálogo traducido y generación de data/cc.json."""
import json
import re
from pathlib import Path

ROOT = Path('.')
SRC = ROOT / 'data/cc_es.json'
OUT = ROOT / 'data/cc.json'

data = json.loads(SRC.read_text(encoding='utf-8'))

CLASS_DESCRIPTIONS = {
    'FAU': 'La auditoría de seguridad permite reconocer, registrar, almacenar y analizar las actividades relevantes para la seguridad. Sus registros ayudan a determinar qué ocurrió y qué usuario es responsable.',
    'FCO': 'Esta clase reúne las familias que garantizan la identidad de las partes de un intercambio de datos: la prueba del origen de la información transmitida y la prueba de su recepción.',
    'FCS': 'Esta clase agrupa los requisitos de las funciones criptográficas que la TOE puede implementar en hardware, firmware o software: gestión de claves, operaciones criptográficas y generación de números aleatorios.',
    'FDP': 'Esta clase especifica cómo se protegen los datos de usuario dentro de la TOE y durante su importación, exportación, almacenamiento y transferencia. Sus familias definen políticas de control de acceso y de flujo de información, y las funciones que las aplican.',
    'FIA': 'Esta clase establece cómo se identifica y autentica a los usuarios, cómo se gestionan sus atributos y cómo se asocian a los sujetos. Una identificación y autenticación correctas son la base para aplicar las políticas de seguridad.',
    'FMT': 'Esta clase define la gestión de la seguridad: roles, atributos de seguridad, datos y funciones de la TSF. Permite especificar quién puede administrar cada elemento y con qué límites.',
    'FPR': 'Esta clase reúne los requisitos de privacidad que protegen la identidad del usuario frente a su descubrimiento o uso indebido por parte de otros usuarios.',
    'FPT': 'Esta clase protege la propia TSF: su integridad, sus datos, su inicialización, su recuperación y su interacción con entidades externas. Complementa a FDP, que se centra en los datos de usuario.',
    'FRU': 'Esta clase respalda la disponibilidad de los recursos de la TOE mediante tolerancia a fallos, prioridades de servicio y asignación de recursos.',
    'FTA': 'Esta clase controla el establecimiento y el uso de las sesiones de usuario en la TOE: límites, bloqueo, terminación, avisos e historial de acceso.',
    'FTP': 'Esta clase exige rutas y canales de comunicación de confianza entre los usuarios y la TSF, y entre la TSF y otros productos de TI de confianza.',
}

FAMILY_DESCRIPTIONS = {
    'FDP_ROL': 'La reversión permite deshacer la última operación o una serie de operaciones, dentro de un límite como un periodo de tiempo, y volver a un estado anterior conocido. Así se preserva la integridad de los datos de usuario.',
    'FMT_SMF': 'Esta familia especifica las funciones de gestión que debe proporcionar la TOE. A través de la interfaz TSFI, los administradores definen los parámetros que controlan los atributos de protección, auditoría, identificación y autenticación, y otras funciones de operación y mantenimiento.',
    'FPT_EMS': 'Esta familia aborda la fuga de información a través de emanaciones observables de la TOE durante su funcionamiento. Define requisitos para limitar las emanaciones inteligibles que podrían permitir ataques como el análisis de potencia o el análisis electromagnético.',
    'FPT_SSP': 'Los protocolos de sincronización de estado permiten que dos partes distribuidas de la TOE acuerden y sincronicen su estado después de una acción relevante para la seguridad. La familia exige que ciertas funciones críticas de la TSF utilicen un protocolo de este tipo.',
    'FTP_PRO': 'Esta familia define los requisitos para establecer un canal de confianza y utilizarlo para transferir datos de la TSF o datos de usuario de forma segura.',
}

SUMMARIES = {
    'FAU_ARP.1': 'Exige que la TSF ejecute acciones cuando detecte una posible violación de la seguridad.',
    'FAU_GEN.1': 'Define el nivel de detalle de los eventos auditables y los datos que deben registrarse en cada registro de auditoría.',
    'FAU_GEN.2': 'Exige que la TSF asocie cada evento auditable con la identidad del usuario que lo provocó.',
    'FAU_SAA.1': 'Exige la detección de umbrales básicos a partir de un conjunto fijo de reglas.',
    'FAU_SAA.2': 'Exige que la TSF mantenga perfiles de uso y calcule una calificación de sospecha para detectar anomalías en la actividad de los usuarios, en tiempo real o por lotes.',
    'FAU_SAA.3': 'Exige que la TSF detecte eventos de firma que representen una amenaza significativa para el cumplimiento de los SFR.',
    'FAU_SAA.4': 'Exige que la TSF represente y detecte escenarios de intrusión de varios pasos comparando secuencias de eventos.',
    'FAU_SAR.1': 'Exige que la TSF permita leer la información contenida en los datos de auditoría.',
    'FAU_SAR.2': 'Exige que solo los usuarios autorizados en FAU_SAR.1 puedan leer los datos de auditoría.',
    'FAU_SAR.3': 'Exige que las herramientas de revisión permitan seleccionar los datos de auditoría que se van a examinar según criterios definidos.',
    'FAU_SEL.1': 'Exige poder seleccionar, entre todos los eventos auditables, el conjunto de eventos que se auditarán según atributos definidos por el autor del PP, módulo de PP, paquete funcional o ST.',
    'FAU_STG.1': 'Exige que se especifiquen las ubicaciones de almacenamiento de los datos de auditoría.',
    'FAU_STG.2': 'Exige proteger los datos de auditoría contra eliminación o modificación no autorizadas.',
    'FAU_STG.3': 'Especifica las garantías que la TSF debe mantener sobre los datos de auditoría ante condiciones no deseadas.',
    'FAU_STG.4': 'Especifica las acciones que deben emprenderse cuando se supera un umbral en el almacenamiento de datos de auditoría.',
    'FAU_STG.5': 'Especifica las acciones que deben emprenderse cuando el almacenamiento de datos de auditoría está lleno.',
    'FCO_NRO.1': 'Exige que la TSF permita a los sujetos solicitar evidencia del origen de la información.',
    'FCO_NRO.2': 'Exige que la TSF genere siempre evidencia del origen de la información transmitida.',
    'FCO_NRR.1': 'Exige que la TSF permita a los sujetos solicitar evidencia de la recepción de la información.',
    'FCO_NRR.2': 'Exige que la TSF genere siempre evidencia de la recepción de la información recibida.',
    'FCS_CKM.1': 'Exige que las claves criptográficas se generen con un algoritmo y unos tamaños de clave especificados, que pueden basarse en un estándar asignado.',
    'FCS_CKM.2': 'Exige que las claves criptográficas se distribuyan mediante un método especificado, que puede basarse en un estándar asignado.',
    'FCS_CKM.3': 'Exige que el acceso a las claves criptográficas se realice mediante un método especificado, que puede basarse en un estándar asignado.',
    'FCS_CKM.4': 'Componente obsoleto. Se conserva el número para mantener la coherencia con ediciones anteriores; en su lugar se utiliza FCS_CKM.6.',
    'FCS_CKM.5': 'Exige que se especifiquen los métodos, estándares y parámetros empleados para derivar claves criptográficas.',
    'FCS_CKM.6': 'Exige que las claves criptográficas se destruyan en el momento y mediante el evento especificados, de acuerdo con métodos de destrucción definidos.',
    'FCS_COP.1': 'Exige que una operación criptográfica se realice con un algoritmo y unos tamaños de clave especificados, que pueden basarse en un estándar asignado.',
    'FCS_RBG.1': 'Exige que la generación de bits aleatorios se realice conforme a estándares seleccionados y especifica la siembra inicial y la actualización del estado del RBG.',
    'FCS_RBG.2': 'Establece requisitos para la siembra de un RBG mediante una fuente de entropía externa a la TOE.',
    'FCS_RBG.3': 'Establece requisitos para la siembra de un RBG mediante una única fuente de entropía de la TSF.',
    'FCS_RBG.4': 'Establece requisitos para la siembra de un RBG mediante múltiples fuentes de entropía de la TSF.',
    'FCS_RBG.5': 'Establece requisitos para combinar varias fuentes de entropía, internas o externas.',
    'FCS_RBG.6': 'Exige que se suministren números aleatorios a través de una interfaz externa como servicio a otras entidades.',
    'FCS_RNG.1': 'Exige que los números aleatorios cumplan una métrica de calidad definida.',
    'FDP_ACC.1': 'Exige que una SFP de control de acceso identificada se aplique a un subconjunto de las operaciones posibles sobre un subconjunto de los objetos de la TOE.',
    'FDP_ACC.2': 'Exige que una SFP de control de acceso cubra todas las operaciones sobre los sujetos y objetos que abarca, y que todos los objetos y operaciones protegidos por la TSF queden cubiertos por al menos una SFP identificada.',
    'FDP_ACF.1': 'Permite que la TSF aplique el control de acceso basándose en atributos de seguridad y en grupos de atributos, y que autorice o deniegue explícitamente el acceso.',
    'FDP_DAU.1': 'Exige que la TSF pueda generar una garantía de autenticidad del contenido de información de los objetos.',
    'FDP_DAU.2': 'Exige además que la TSF pueda establecer la identidad del sujeto que proporcionó la garantía de autenticidad.',
    'FDP_ETC.1': 'Exige que la TSF aplique las SFP correspondientes al exportar datos de usuario fuera de la TSF, sin sus atributos de seguridad asociados.',
    'FDP_ETC.2': 'Exige que la TSF aplique las SFP correspondientes al exportar datos de usuario y asocie de forma precisa e inequívoca sus atributos de seguridad.',
    'FDP_IFC.1': 'Exige que una SFP de control de flujo de información identificada se aplique a un subconjunto de las operaciones posibles sobre un subconjunto de los flujos de información de la TOE.',
    'FDP_IFC.2': 'Exige que una SFP de control de flujo de información cubra todas las operaciones sobre los sujetos e información que abarca, y que todos los flujos y operaciones controlados por la TSF queden cubiertos por al menos una SFP identificada.',
    'FDP_IFF.1': 'Exige atributos de seguridad sobre la información y sobre los sujetos que la originan o reciben, y especifica las reglas que la función debe aplicar y cómo se derivan dichos atributos.',
    'FDP_IFF.2': 'Amplía FDP_IFF.1 exigiendo que las SFP de control de flujo de información utilicen atributos de seguridad jerárquicos y reglas coherentes.',
    'FDP_IFF.3': 'Exige que la SFP cubra los flujos de información ilícitos, sin exigir necesariamente su eliminación.',
    'FDP_IFF.4': 'Exige que la SFP cubra la eliminación de algunos flujos de información ilícitos, no necesariamente todos.',
    'FDP_IFF.5': 'Exige que la SFP cubra la eliminación de todos los flujos de información ilícitos.',
    'FDP_IFF.6': 'Exige que la SFP supervise los flujos de información ilícitos para capacidades especificadas y máximas.',
    'FDP_IRC.1': 'Exige que la TSF elimine las copias de un conjunto definido de objetos cuando ya no sean estrictamente necesarias y que identifique las operaciones que las requieren.',
    'FDP_ITC.1': 'Exige que los atributos de seguridad representen correctamente los datos de usuario y se suministren por separado del objeto al importarlos.',
    'FDP_ITC.2': 'Exige que los atributos de seguridad representen correctamente los datos de usuario y se asocien de forma precisa e inequívoca al importarlos desde fuera de la TOE.',
    'FDP_ITT.1': 'Exige que los datos de usuario se protejan cuando se transmiten entre partes de la TOE.',
    'FDP_ITT.2': 'Exige separar los datos según el valor de los atributos relevantes para la SFP, además de la protección básica.',
    'FDP_ITT.3': 'Exige que la TSF supervise los datos de usuario transmitidos entre partes de la TOE para detectar errores de integridad identificados.',
    'FDP_ITT.4': 'Amplía FDP_ITT.3 permitiendo que la forma de supervisión de integridad varíe según los atributos relevantes para la SFP.',
    'FDP_RIP.1': 'Exige que la TSF garantice que el contenido residual de un recurso no esté disponible para un subconjunto definido de objetos al asignarlo o liberarlo.',
    'FDP_RIP.2': 'Exige que la TSF garantice que el contenido residual de un recurso no esté disponible para ningún objeto al asignarlo o liberarlo.',
    'FDP_ROL.1': 'Exige poder revertir o deshacer un número limitado de operaciones dentro de los límites definidos.',
    'FDP_ROL.2': 'Exige poder revertir o deshacer todas las operaciones dentro de los límites definidos.',
    'FDP_SDC.1': 'Exige que la TSF proteja la confidencialidad de la información de los datos de usuario en áreas de memoria especificadas.',
    'FDP_SDC.2': 'Exige que la TSF proteja la confidencialidad de los datos de usuario según sus características, mediante un método de protección dedicado.',
    'FDP_SDI.1': 'Exige que la TSF supervise los datos de usuario almacenados en contenedores que controla para detectar errores de integridad identificados.',
    'FDP_SDI.2': 'Amplía FDP_SDI.1 permitiendo que la TSF emprenda acciones cuando detecte un error de integridad.',
    'FDP_UCT.1': 'Exige proteger los datos de usuario contra su divulgación durante la transmisión.',
    'FDP_UIT.1': 'Exige detectar modificaciones, eliminaciones, inserciones y repeticiones en los datos de usuario transmitidos.',
    'FDP_UIT.2': 'Exige que la TSF receptora pueda recuperar los datos de usuario originales con ayuda del producto de TI de confianza de origen.',
    'FDP_UIT.3': 'Exige que la TSF receptora pueda recuperar los datos de usuario originales por sí sola, sin ayuda del producto de origen.',
    'FIA_AFL.1': 'Exige que la TSF pueda terminar el proceso de establecimiento de sesión tras un número especificado de intentos fallidos de autenticación y, después, deshabilitar la cuenta o el punto de entrada hasta que se cumpla una condición definida por el administrador.',
    'FIA_API.1': 'Proporciona prueba de la identidad de la TOE ante una entidad externa.',
    'FIA_ATD.1': 'Permite mantener individualmente los atributos de seguridad de cada usuario.',
    'FIA_SOS.1': 'Exige que la TSF verifique que los secretos cumplen métricas de calidad definidas.',
    'FIA_SOS.2': 'Exige que la TSF pueda generar secretos que cumplan métricas de calidad definidas.',
    'FIA_UAU.1': 'Permite que un usuario realice determinadas acciones antes de que la TSF autentique su identidad.',
    'FIA_UAU.2': 'Exige que los usuarios se autentiquen antes de que la TSF permita cualquier otra acción.',
    'FIA_UAU.3': 'Exige que el mecanismo de autenticación detecte y prevenga el uso de datos de autenticación falsificados o copiados.',
    'FIA_UAU.4': 'Exige un mecanismo de autenticación basado en datos de autenticación de un solo uso.',
    'FIA_UAU.5': 'Exige disponer de distintos mecanismos de autenticación y utilizarlos para autenticar identidades de usuario en eventos específicos.',
    'FIA_UAU.6': 'Exige poder especificar los eventos para los que el usuario debe volver a autenticarse.',
    'FIA_UAU.7': 'Exige que durante la autenticación solo se proporcione al usuario información de retorno limitada.',
    'FIA_UID.1': 'Permite que los usuarios realicen determinadas acciones antes de que la TSF los identifique.',
    'FIA_UID.2': 'Exige que los usuarios se identifiquen antes de que la TSF permita cualquier acción.',
    'FIA_USB.1': 'Exige especificar las reglas que rigen la asociación entre los atributos de usuario y los atributos del sujeto a los que se asignan.',
    'FMT_LIM.1': 'Exige que la TSF se construya con solo las capacidades necesarias para su propósito legítimo.',
    'FMT_LIM.2': 'Exige que la TSF restrinja el uso de sus funciones a las necesarias para su propósito legítimo y limite su disponibilidad.',
    'FMT_MOF.1': 'Permite que los usuarios autorizados (roles) gestionen el comportamiento de las funciones de la TSF que usan reglas o condiciones especificadas.',
    'FMT_MSA.1': 'Permite que los usuarios autorizados (roles) gestionen los atributos de seguridad especificados.',
    'FMT_MSA.2': 'Exige que los valores asignados a los atributos de seguridad sean válidos respecto del estado seguro.',
    'FMT_MSA.3': 'Exige que los valores predeterminados de los atributos de seguridad sean adecuadamente permisivos o restrictivos.',
    'FMT_MSA.4': 'Permite especificar las reglas o políticas que determinan el valor que hereda un atributo de seguridad.',
    'FMT_MTD.1': 'Permite que los usuarios autorizados gestionen los datos de la TSF.',
    'FMT_MTD.2': 'Especifica las acciones que deben emprenderse cuando se alcanzan o superan los límites sobre los datos de la TSF.',
    'FMT_MTD.3': 'Exige que los valores asignados a los datos de la TSF sean válidos respecto del estado seguro.',
    'FMT_REV.1': 'Exige que la revocación de los atributos de seguridad se aplique en un momento determinado.',
    'FMT_SAE.1': 'Permite que un usuario autorizado especifique una fecha de caducidad para determinados atributos de seguridad.',
    'FMT_SMF.1': 'Exige que la TSF proporcione funciones de gestión específicas.',
    'FMT_SMR.1': 'Especifica los roles de seguridad que reconoce la TSF.',
    'FMT_SMR.2': 'Especifica reglas que, además de definir los roles, controlan las relaciones entre ellos.',
    'FMT_SMR.3': 'Exige que la TSF reciba una solicitud explícita para asumir un rol.',
    'FPR_ANO.1': 'Exige que otros usuarios o sujetos no puedan determinar la identidad de un usuario asociado a un sujeto u operación.',
    'FPR_ANO.2': 'Amplía FPR_ANO.1 garantizando que la TSF no solicite la identidad del usuario.',
    'FPR_PSE.1': 'Exige que un conjunto de usuarios y/o sujetos no pueda determinar la identidad de un usuario, pero que este siga siendo responsable de sus acciones.',
    'FPR_PSE.2': 'Exige que la TSF pueda determinar la identidad original del usuario a partir de un alias proporcionado.',
    'FPR_PSE.3': 'Exige que la TSF aplique reglas de construcción determinadas al alias de la identidad del usuario.',
    'FPR_UNL.1': 'Exige que los usuarios y/o sujetos no puedan determinar si el mismo usuario causó ciertas operaciones o si están relacionadas.',
    'FPR_UNO.1': 'Exige que los usuarios y/o sujetos no puedan determinar si se está realizando una operación.',
    'FPR_UNO.2': 'Exige que la TSF evite la concentración de información relacionada con la privacidad dentro de la TOE.',
    'FPR_UNO.3': 'Exige que la TSF no intente obtener información relacionada con la privacidad que pueda comprometer la no observabilidad.',
    'FPR_UNO.4': 'Exige que la TSF permita a uno o más usuarios autorizados observar el uso de recursos y/o servicios.',
    'FPT_EMS.1': 'Define requisitos para que la TOE mitigue las emanaciones inteligibles de la TSF y de los datos de usuario.',
    'FPT_FLS.1': 'Exige que la TSF preserve un estado seguro ante los fallos identificados.',
    'FPT_INI.1': 'Exige que la TOE proporcione una función de inicialización que lleve a la TSF a un estado operativo seguro al encenderse.',
    'FPT_ITA.1': 'Exige que la TSF garantice, con un grado de probabilidad identificado, la disponibilidad de los datos de la TSF proporcionados a otro producto de TI de confianza.',
    'FPT_ITC.1': 'Exige que la TSF proteja los datos transmitidos entre ella y otro producto de TI de confianza contra su divulgación durante el tránsito.',
    'FPT_ITI.1': 'Permite detectar modificaciones de los datos de la TSF durante la transmisión entre la TSF y otro producto de TI de confianza.',
    'FPT_ITI.2': 'Permite a otro producto de TI de confianza no solo detectar modificaciones de los datos de la TSF, sino también corregirlas.',
    'FPT_ITT.1': 'Exige que los datos de la TSF se protejan cuando se transmiten entre partes separadas de la TOE.',
    'FPT_ITT.2': 'Exige que la TSF separe los datos de usuario de los datos de la TSF durante la transmisión.',
    'FPT_ITT.3': 'Exige que los datos de la TSF transmitidos entre partes separadas de la TOE se supervisen para detectar errores de integridad identificados.',
    'FPT_PHP.1': 'Proporciona funciones que indican cuándo un dispositivo o elemento de la TSF ha sufrido manipulación; la notificación no es automática, sino que la invoca un usuario autorizado o una inspección manual.',
    'FPT_PHP.2': 'Proporciona notificación automática de manipulación para un subconjunto identificado de penetraciones físicas.',
    'FPT_PHP.3': 'Proporciona funciones que previenen o resisten la manipulación física de dispositivos y elementos de la TSF.',
    'FPT_RCV.1': 'Permite que la TOE solo proporcione mecanismos que requieran intervención humana para volver a un estado seguro.',
    'FPT_RCV.2': 'Proporciona recuperación automática a un estado seguro para al menos un tipo de interrupción del servicio, y recuperación con posible intervención humana para otros tipos.',
    'FPT_RCV.3': 'Proporciona recuperación automática y prohíbe la pérdida indebida de objetos protegidos.',
    'FPT_RCV.4': 'Proporciona recuperación a nivel de funciones concretas, garantizando su finalización correcta o la reversión de los datos de la TSF a un estado seguro.',
    'FPT_RPL.1': 'Exige que la TSF pueda detectar la repetición de entidades identificadas.',
    'FPT_SSP.1': 'Exige únicamente un acuse de recibo simple por parte del destinatario de los datos.',
    'FPT_SSP.2': 'Exige un acuse de recibo mutuo del intercambio de datos.',
    'FPT_STM.1': 'Exige que la TSF proporcione marcas de tiempo fiables para las funciones de la TSF.',
    'FPT_STM.2': 'Exige que se describa la fuente de tiempo utilizada para generar las marcas de tiempo.',
    'FPT_TDC.1': 'Exige que la TSF pueda garantizar la coherencia de los atributos entre TSF.',
    'FPT_TEE.1': 'Permite que la TSF pruebe entidades externas.',
    'FPT_TRC.1': 'Exige que la TSF garantice la coherencia de los datos de la TSF replicados en varias ubicaciones.',
    'FPT_TST.1': 'Permite comprobar el funcionamiento correcto de la TSF al inicio, periódicamente, a solicitud de un usuario autorizado o cuando se cumplan otras condiciones, y verificar la integridad de los datos de la TSF y de la propia TSF.',
    'FRU_FLT.1': 'Exige que la TOE mantenga el funcionamiento correcto de las capacidades identificadas ante fallos identificados.',
    'FRU_FLT.2': 'Exige que la TOE mantenga el funcionamiento correcto de todas sus capacidades ante fallos identificados.',
    'FRU_PRS.1': 'Proporciona prioridades para el uso, por parte de un sujeto, de un subconjunto de los recursos controlados por la TSF.',
    'FRU_PRS.2': 'Proporciona prioridades para el uso, por parte de un sujeto, de todos los recursos controlados por la TSF.',
    'FRU_RSA.1': 'Exige mecanismos de cuota que impidan que usuarios y sujetos monopolicen un recurso controlado.',
    'FRU_RSA.2': 'Exige mecanismos de cuota que garanticen un mínimo de un recurso especificado y eviten que usuarios y sujetos lo monopolicen.',
    'FTA_LSA.1': 'Exige que la TOE limite el alcance de los atributos de seguridad de sesión durante el establecimiento de la sesión.',
    'FTA_MCS.1': 'Establece limitaciones al número de sesiones simultáneas que se aplican a todos los usuarios de la TSF.',
    'FTA_MCS.2': 'Amplía FTA_MCS.1 permitiendo especificar limitaciones al número de sesiones simultáneas según atributos de seguridad del usuario.',
    'FTA_SSL.1': 'Incluye el bloqueo iniciado por el sistema de una sesión interactiva tras un periodo especificado de inactividad del usuario.',
    'FTA_SSL.2': 'Permite que el usuario bloquee y desbloquee sus propias sesiones interactivas.',
    'FTA_SSL.3': 'Exige que la TSF termine la sesión tras un periodo especificado de inactividad del usuario.',
    'FTA_SSL.4': 'Permite que el usuario termine sus propias sesiones interactivas.',
    'FTA_TAB.1': 'Exige que la TOE muestre un aviso de acceso antes de iniciar el diálogo de establecimiento de una sesión.',
    'FTA_TAH.1': 'Exige que la TOE muestre información sobre intentos anteriores de establecer una sesión.',
    'FTA_TSE.1': 'Exige que la TOE deniegue el acceso de usuarios a la TOE en función de determinados atributos.',
    'FTP_ITC.1': 'Exige que la TSF proporcione un canal de comunicación de confianza entre ella y otro producto de TI de confianza.',
    'FTP_PRO.1': 'Exige que la comunicación se establezca conforme a un protocolo definido.',
    'FTP_PRO.2': 'Exige que las claves se establezcan de forma segura entre los pares.',
    'FTP_PRO.3': 'Exige que los datos en tránsito estén protegidos.',
    'FTP_TRP.1': 'Exige que se proporcione una ruta de confianza entre la TSF y un usuario para un conjunto de eventos definido por el autor del PP, módulo de PP, paquete funcional o ST.',
}

ELEMENTS = {
    'FPT_EMS.1.1': [
        {'type': 'p', 'text': 'La TSF deberá garantizar que la TOE no emita emanaciones a través de su superficie de ataque en una cantidad tal que permitan acceder a los datos de la TSF y a los datos de usuario, según se especifica en la Tabla 1.'},
        {'type': 'list', 'ordered': False, 'items': [
            'Emisiones: [asignación: lista de tipos de emisiones].',
            'Superficie de ataque: [asignación: lista de tipos de superficie de ataque].',
            'Datos de la TSF: [asignación: lista de tipos de datos de la TSF].',
            'Datos de usuario: [asignación: lista de tipos de datos de usuario].',
        ]},
    ],
    'FPT_INI.1.2': [
        {'type': 'p', 'text': 'La función de inicialización de la TOE deberá garantizar que ciertas propiedades se mantengan sobre ciertos elementos inmediatamente antes de establecer la TSF en un estado inicial seguro, según se especifica en la Tabla 2.'},
        {'type': 'list', 'ordered': False, 'items': [
            'Propiedades: [asignación: propiedad; por ejemplo, autenticidad, integridad o versión correcta de la TSF o del usuario].',
            'Elementos: [asignación: lista de firmware, software o datos de la TSF o del usuario].',
        ]},
    ],
    'FTP_TRP.1.3': [
        {'type': 'p', 'text': 'La TSF deberá exigir el uso de la ruta de confianza para [selección: autenticación inicial del usuario, [asignación: otros servicios para los cuales se requiere una ruta de confianza]].'},
    ],
    'FPT_STM.1.1': [
        {'type': 'p', 'text': 'La TSF deberá poder proporcionar marcas de tiempo fiables.'},
    ],
    'FPT_STM.2.1': [
        {'type': 'p', 'text': 'La TSF deberá permitir que [asignación: usuario autorizado por la política de seguridad] [asignación: establezca la hora o configure otra fuente de tiempo].'},
    ],
    'FPT_TEE.1.2': [
        {'type': 'p', 'text': 'Si la prueba falla, la TSF deberá [asignación: acción o acciones].'},
    ],
}

GLOBAL_REPLACEMENTS = [
    ('datos de TSF', 'datos de la TSF'),
    ('datos TSF', 'datos de la TSF'),
    ('las SFR', 'los SFR'),
    ('el SFR', 'el SFR'),
    ('tema de la TSF', 'sujeto de la TSF'),
    ('iniciador y objetivo', 'iniciador y destino'),
    ('objetivos políticos', 'objetivos de la política'),
    ('Acciones a tomar', 'Acciones adoptadas'),
    ('acciones a tomar', 'acciones adoptadas'),
    ('en base a', 'según'),
    ('Bien formado de las reglas', 'Corrección formal de las reglas'),
    ('Intenta reutilizar', 'Intento de reutilizar'),
    ('No recibir un acuse', 'No recepción de un acuse'),
    ('capacidades TOE', 'capacidades de la TOE'),
    ('un SFP', 'una SFP'),
    ('el SFP', 'la SFP'),
    ('del SFP', 'de la SFP'),
    ('al SFP', 'a la SFP'),
    ('este SFP', 'esta SFP'),
    ('ese SFP', 'esa SFP'),
    ('los SFP', 'las SFP'),
    ('SFP identificado', 'SFP identificada'),
    ('SFP de control de acceso determinado', 'SFP de control de acceso determinada'),
    ('SFP de control de flujo de información determinado', 'SFP de control de flujo de información determinada'),
    ('La función de inicialización TOE', 'La función de inicialización de la TOE'),
    ('función de inicialización TOE', 'función de inicialización de la TOE'),
    ('del propio TSF', 'de la propia TSF'),
    ('el propio TSF', 'la propia TSF'),
    ('Se generará la identidad del usuario que solicitó que se genere evidencia de procedencia', 'Identidad del usuario que solicitó la generación de evidencia de origen'),
    ('Se generará la identidad del usuario que solicitó que se genere evidencia de recepción', 'Identidad del usuario que solicitó la generación de evidencia de recepción'),
    ('Alcanzar el umbral de los intentos fallidos de autenticación y de las acciones adoptadas y el posterior, en su caso, restablecimiento al estado normal.', 'Alcance del umbral de intentos fallidos de autenticación, acciones adoptadas y, en su caso, restablecimiento al estado normal.'),
    ('Todas las capacidades TOE se suspenderán debido a una falla.', 'Suspensión de todas las capacidades de la TOE debido a una falla.'),
    ('El sujeto/usuario que solicitó la resolución de la identidad del usuario deberá ser auditado.', 'Identidad del sujeto o usuario que solicitó la resolución de la identidad.'),
    ('La ausencia de datos de la TSF cuando los requiera una TOE.', 'Ausencia de datos de la TSF cuando los requiera la TOE.'),
    ('Fallos al intentar verificar las propiedades del canal en FTP_PRO.3.2.', 'Fallos al verificar las propiedades del canal en FTP_PRO.3.2.'),
    ('Cualquier modo(s) de operación criptográfico aplicable, atributos de sujeto y atributos de objeto.', 'Cualquier modo de operación criptográfico aplicable, atributos del sujeto y atributos del objeto.'),
    ('Especificación del tiempo de vencimiento de un atributo;', 'Especificación del tiempo de caducidad de un atributo;'),
    ('El resultado de cada mecanismo activado junto con la decisión final.', 'Resultado de cada mecanismo activado junto con la decisión final.'),
    ('Se deberá considerar otros eventos', 'Se deberán considerar otros eventos'),
]

NAME_FIXES = {
    'FPT_INI.1': 'Inicialización de la TSF',
    'FPT_EMS': 'Emanación de la TOE',
}

# Remove any residue from the extraction of tables and annexes.
def clean_text(text):
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text or '')
    text = re.sub(r'\s+', ' ', text).strip()
    for old, new in GLOBAL_REPLACEMENTS:
        text = text.replace(old, new)
    return text

for cls in data['classes']:
    cls['name'] = NAME_FIXES.get(cls['id'], cls['name'])
    cls['description'] = clean_text(CLASS_DESCRIPTIONS.get(cls['id'], cls['description']))
    cls['keywords'] = []
    for fam in cls['families']:
        fam['name'] = NAME_FIXES.get(fam['id'], fam['name'])
        fam['description'] = clean_text(FAMILY_DESCRIPTIONS.get(fam['id'], fam['description']))
        fam['keywords'] = []
        for comp in fam['components']:
            comp['name'] = NAME_FIXES.get(comp['id'], comp['name'])
            comp['summary'] = clean_text(SUMMARIES.get(comp['id'], comp['summary']))
            comp['available'] = True
            comp['keywords'] = []
            for element in comp['elements']:
                if element['id'] in ELEMENTS:
                    element['blocks'] = ELEMENTS[element['id']]
                for block in element['blocks']:
                    if block['type'] == 'p':
                        block['text'] = clean_text(block['text'])
                    else:
                        block['items'] = [clean_text(x) for x in block['items']]
            comp['management'] = [clean_text(x) for x in comp['management']]
            for audit in comp['audit']:
                audit['text'] = clean_text(audit['text'])
                if audit['text'].startswith('Bbasic:'):
                    audit['level'] = 'básico'
                    audit['text'] = audit['text'][len('Bbasic:'):].strip()
                    if audit['text']:
                        audit['text'] = audit['text'][0].upper() + audit['text'][1:]

# Keywords: names + distinctive terms from the summary.
STOP = set('''a al algo algunas algunos ante antes como con contra cual cuales cuando de del desde donde durante e el ella ellas ellos en entre era es esa esas ese eso esos esta estas este esto estos fue ha hasta hay la las le les lo los mas más me mi mis muy no nos o otra otras otro otros para pero poco por porque que quien quienes se sea ser si sin sobre son su sus tambien también tanto te tiene tienen todo todos tu tus un una unas uno unos y ya
ser estar haber tener hacer poder deber deberá deberán tsf toe sfp sfr componente componentes familia clases clase requisito requisitos seguridad sistema usuario usuarios datos información información'''.split())

KEYWORDS_CLASS = {
    'FAU': ['auditoría', 'registros', 'eventos', 'revisión', 'alertas'],
    'FCO': ['no repudio', 'origen', 'recepción', 'evidencia', 'comunicación'],
    'FCS': ['criptografía', 'claves', 'cifrado', 'aleatoriedad', 'firmas'],
    'FDP': ['datos de usuario', 'control de acceso', 'flujo de información', 'integridad', 'confidencialidad'],
    'FIA': ['identificación', 'autenticación', 'atributos', 'sesiones', 'credenciales'],
    'FMT': ['gestión', 'roles', 'atributos', 'funciones', 'administración'],
    'FPR': ['privacidad', 'anonimato', 'seudónimo', 'no observabilidad', 'no vinculabilidad'],
    'FPT': ['protección de la TSF', 'integridad', 'inicialización', 'recuperación', 'autoprueba'],
    'FRU': ['recursos', 'tolerancia a fallos', 'prioridad', 'cuotas', 'disponibilidad'],
    'FTA': ['sesiones', 'acceso', 'bloqueo', 'terminación', 'avisos'],
    'FTP': ['canal de confianza', 'ruta de confianza', 'comunicación segura', 'protocolo', 'inter-TSF'],
}

KEYWORDS_FAMILY = {
    'FAU_ARP': ['alarmas', 'respuesta', 'violación', 'eventos'],
    'FAU_GEN': ['registro', 'eventos auditables', 'nivel de auditoría'],
    'FAU_SAA': ['análisis', 'intrusiones', 'anomalías', 'heurísticas'],
    'FAU_SAR': ['revisión', 'lectura', 'herramientas', 'auditoría'],
    'FAU_SEL': ['selección', 'eventos', 'filtros', 'auditoría'],
    'FAU_STG': ['almacenamiento', 'protección', 'disponibilidad', 'pérdida'],
    'FCO_NRO': ['origen', 'evidencia', 'no repudio'],
    'FCO_NRR': ['recepción', 'evidencia', 'no repudio'],
    'FCS_CKM': ['claves', 'generación', 'distribución', 'destrucción', 'derivación'],
    'FCS_COP': ['operación criptográfica', 'cifrado', 'firma', 'hash'],
    'FCS_RBG': ['bits aleatorios', 'entropía', 'siembra', 'RBG'],
    'FCS_RNG': ['números aleatorios', 'calidad', 'RNG'],
    'FDP_ACC': ['control de acceso', 'SFP', 'sujetos', 'objetos'],
    'FDP_ACF': ['reglas de acceso', 'atributos', 'autorización', 'denegación'],
    'FDP_DAU': ['autenticidad', 'datos', 'garante'],
    'FDP_ETC': ['exportación', 'datos de usuario', 'atributos'],
    'FDP_IFC': ['flujo de información', 'SFP', 'sujetos', 'operaciones'],
    'FDP_IFF': ['flujo de información', 'atributos', 'canales encubiertos'],
    'FDP_IRC': ['retención', 'eliminación', 'objetos', 'datos'],
    'FDP_ITC': ['importación', 'datos de usuario', 'atributos'],
    'FDP_ITT': ['transferencia interna', 'integridad', 'separación'],
    'FDP_RIP': ['información residual', 'recursos', 'liberación'],
    'FDP_ROL': ['reversión', 'deshacer', 'operaciones', 'límites'],
    'FDP_SDC': ['confidencialidad', 'almacenamiento', 'memoria'],
    'FDP_SDI': ['integridad', 'almacenamiento', 'errores'],
    'FDP_UCT': ['confidencialidad', 'transferencia', 'inter-TSF'],
    'FDP_UIT': ['integridad', 'transferencia', 'recuperación', 'inter-TSF'],
    'FIA_AFL': ['fallos', 'autenticación', 'intentos', 'bloqueo'],
    'FIA_API': ['prueba de identidad', 'TOE', 'entidad externa'],
    'FIA_ATD': ['atributos', 'usuario', 'identidad'],
    'FIA_SOS': ['secretos', 'calidad', 'verificación', 'generación'],
    'FIA_UAU': ['autenticación', 'mecanismos', 'reautenticación'],
    'FIA_UID': ['identificación', 'usuario', 'momento'],
    'FIA_USB': ['usuario', 'sujeto', 'vinculación', 'atributos'],
    'FMT_LIM': ['capacidades', 'disponibilidad', 'límites'],
    'FMT_MOF': ['funciones', 'comportamiento', 'gestión'],
    'FMT_MSA': ['atributos', 'gestión', 'inicialización', 'herencia'],
    'FMT_MTD': ['datos de la TSF', 'gestión', 'límites'],
    'FMT_REV': ['revocación', 'atributos', 'tiempo'],
    'FMT_SAE': ['caducidad', 'atributos', 'tiempo'],
    'FMT_SMF': ['funciones de gestión', 'TSFI', 'administración'],
    'FMT_SMR': ['roles', 'seguridad', 'asignación'],
    'FPR_ANO': ['anonimato', 'identidad', 'privacidad'],
    'FPR_PSE': ['seudónimo', 'alias', 'privacidad'],
    'FPR_UNL': ['no vinculabilidad', 'operaciones', 'privacidad'],
    'FPR_UNO': ['no observabilidad', 'operaciones', 'privacidad'],
    'FPT_EMS': ['emanaciones', 'TOE', 'ataques físicos'],
    'FPT_FLS': ['fallos', 'estado seguro', 'SFR'],
    'FPT_INI': ['inicialización', 'estado seguro', 'arranque'],
    'FPT_ITA': ['disponibilidad', 'datos de la TSF', 'inter-TSF'],
    'FPT_ITC': ['confidencialidad', 'datos de la TSF', 'transmisión'],
    'FPT_ITI': ['integridad', 'modificaciones', 'transmisión'],
    'FPT_ITT': ['transferencia interna', 'datos de la TSF', 'separación'],
    'FPT_PHP': ['protección física', 'manipulación', 'dispositivos'],
    'FPT_RCV': ['recuperación', 'estado seguro', 'fallos'],
    'FPT_RPL': ['repetición', 'detección', 'replay'],
    'FPT_SSP': ['sincronización', 'estado', 'protocolo'],
    'FPT_STM': ['marcas de tiempo', 'fuente de tiempo', 'fiabilidad'],
    'FPT_TDC': ['coherencia', 'atributos', 'inter-TSF'],
    'FPT_TEE': ['pruebas', 'entidades externas', 'diagnóstico'],
    'FPT_TRC': ['coherencia', 'replicación', 'datos de la TSF'],
    'FPT_TST': ['autoprueba', 'integridad', 'funcionamiento'],
    'FRU_FLT': ['tolerancia a fallos', 'disponibilidad', 'capacidades'],
    'FRU_PRS': ['prioridad', 'servicio', 'recursos'],
    'FRU_RSA': ['cuotas', 'recursos', 'monopolio'],
    'FTA_LSA': ['sesión', 'atributos', 'alcance'],
    'FTA_MCS': ['sesiones simultáneas', 'límites', 'usuario'],
    'FTA_SSL': ['bloqueo', 'terminación', 'inactividad'],
    'FTA_TAB': ['avisos', 'acceso', 'TOE'],
    'FTA_TAH': ['historial', 'acceso', 'sesiones'],
    'FTA_TSE': ['establecimiento', 'sesión', 'atributos'],
    'FTP_ITC': ['canal de confianza', 'inter-TSF', 'comunicación'],
    'FTP_PRO': ['protocolo', 'canal de confianza', 'claves'],
    'FTP_TRP': ['ruta de confianza', 'usuario', 'comunicación'],
}

for cls in data['classes']:
    cls['keywords'] = KEYWORDS_CLASS.get(cls['id'], [])
    for fam in cls['families']:
        fam['keywords'] = KEYWORDS_FAMILY.get(fam['id'], [])
        for comp in fam['components']:
            terms = []
            for source in (comp['name'], comp['summary']):
                for word in re.findall(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ-]{3,}', source):
                    low = word.lower()
                    if low in STOP or len(low) < 4:
                        continue
                    if low not in terms:
                        terms.append(low)
            comp['keywords'] = terms[:6]

data['meta'].update({
    'demo': False,
    'demoNote': '',
    'documentCounts': {'classes': 11, 'families': 74, 'components': 156, 'elements': 284},
    'translationNote': 'Traducción de estudio no oficial. En caso de discrepancia, prevalece el texto oficial en inglés del CCMB.',
})

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print('written', OUT)

# Validation
classes = data['classes']
components = [c for cls in classes for f in cls['families'] for c in f['components']]
elements = [e for c in components for e in c['elements']]
print('counts', len(classes), sum(len(c['families']) for c in classes), len(components), len(elements))
print('summaries', sum(1 for c in components if c.get('summary')))
print('available', sum(1 for c in components if c.get('available')))
missing = [c['id'] for c in components if c['id'] not in SUMMARIES]
print('summary overrides missing', missing)
