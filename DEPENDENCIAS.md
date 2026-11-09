# Dependencias compartidas y compatibilidad en iOS

Esta guía corresponde a la integración de Become `3.5.1-rc.1` mediante Swift Package Manager (SPM). SPM descarga automáticamente sus dependencias; el inventario permite compararlas con paquetes que tu aplicación ya utiliza.

## Qué sucede cuando la app comparte un paquete

SPM resuelve una versión por identidad de paquete que satisfaga los requisitos de todo el proyecto. Si tu app y otra dependencia requieren el mismo paquete, sus rangos o versiones exactas deben tener una intersección. Una versión exacta incompatible puede impedir la resolución antes de compilar.

La descarga automática no asegura compatibilidad con cualquier combinación de bibliotecas de la app. Revisa los requisitos de tus paquetes y las versiones finales en **Package Dependencies** y `Package.resolved`. Una copia manual del mismo módulo o su incorporación por otro gestor también puede producir duplicados; conserva una sola forma compatible de integrarlo.

## Versiones de referencia

Los siguientes paquetes de uso general están presentes en la resolución de referencia del paquete público de esta entrega. Son versiones observadas, no instrucciones para agregarlos manualmente ni un listado de todos los componentes del producto. Estar en la resolución no implica que todos sus productos se enlacen a la app; eso depende de los productos y targets utilizados.

| Identidad del paquete | Versión resuelta de referencia |
| --- | --- |
| `async-http-client` | `1.37.0` |
| `grpc-swift` | `1.26.1` |
| `opentelemetry-swift` | `1.17.1` |
| `opentracing-objc` | `0.5.2` |
| `smithy-swift` | `0.175.0` |
| `sqlite.swift` | `0.15.3` |
| `swift-algorithms` | `1.2.1` |
| `swift-argument-parser` | `1.8.2` |
| `swift-asn1` | `1.7.4` |
| `swift-async-algorithms` | `1.1.7` |
| `swift-atomics` | `1.3.1` |
| `swift-certificates` | `1.21.1` |
| `swift-collections` | `1.7.5` |
| `swift-configuration` | `1.5.0` |
| `swift-crypto` | `5.1.1` |
| `swift-distributed-tracing` | `1.7.4` |
| `swift-http-structured-headers` | `1.7.0` |
| `swift-http-types` | `1.8.0` |
| `swift-log` | `1.17.0` |
| `swift-metrics` | `2.13.0` |
| `swift-nio` | `2.105.0` |
| `swift-nio-extras` | `1.35.2` |
| `swift-nio-http2` | `1.46.0` |
| `swift-nio-ssl` | `2.37.6` |
| `swift-nio-transport-services` | `1.28.0` |
| `swift-numerics` | `1.1.1` |
| `swift-protobuf` | `1.39.0` |
| `swift-service-context` | `1.5.1` |
| `swift-service-lifecycle` | `2.13.0` |
| `swift-system` | `1.8.1` |
| `thrift-swift` | `1.1.2` |

En esta entrega, `sqlite.swift` tiene un requisito transitivo exacto `0.15.3`, y `grpc-swift` uno exacto `1.26.1`. Si tu app solicita esos mismos paquetes, debe admitir esas versiones. Para estos dos requisitos, el límite inferior y el superior de resolución coinciden con la versión exacta indicada; esto describe la regla de SPM, no un intervalo de compatibilidad funcional.

Los demás valores de la tabla son el resultado observado. El intervalo admisible depende de la intersección de los manifiestos de todos los paquetes del proyecto y puede variar al cambiar una dependencia de tu app.

## Mínimos y máximos de compatibilidad

| Dato | Alcance |
| --- | --- |
| Versión resuelta de referencia | La indicada para cada paquete en la resolución de referencia. |
| Mínimo funcional compatible | No establecido para paquetes con requisitos flexibles. |
| Máximo funcional compatible | No establecido. |
| Versión de BecomeDigital | Fija `3.5.1-rc.1` como se indica en la [instalación](INSTALACION.md). |

Una resolución válida confirma que los requisitos declarados se pueden satisfacer. No certifica por sí sola la compilación ni el comportamiento de todas las bibliotecas de tu aplicación. Tampoco permite concluir que una versión anterior o posterior sea compatible o esté deprecada.

## Revisar tu integración

1. Compara las identidades que tu app usa directamente con este inventario y revisa sus reglas de versión.
2. Resuelve los paquetes en Xcode y consulta el conjunto final en `Package.resolved`; conserva ese archivo junto con tu proyecto para reproducirlo.
3. Si Xcode informa requisitos incompatibles, identifica las dos restricciones y ajusta las dependencias de tu app a una versión común. Si no existe una combinación aceptable para tu proyecto, consulta con soporte la entrega de BecomeDigital que corresponda.
4. Compila para los destinos de tu app y prueba la configuración de publicación en un dispositivo físico: permisos, captura documental, validación facial, cancelación y resultados.

Para solicitar soporte, comparte la versión de BecomeDigital, las versiones de Xcode/iOS, el error de resolución o enlace y los paquetes que coinciden con el inventario. Omite credenciales, datos de usuarios y el contenido de la licencia de la app.

Consulta la documentación de [dependencias y requisitos de versión de Swift Package Manager](https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html) y la [gestión de paquetes en Xcode](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app).
