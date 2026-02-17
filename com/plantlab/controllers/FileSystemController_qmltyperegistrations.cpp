/****************************************************************************
** Generated QML type registration code
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <QtQml/qqml.h>
#include <QtQml/qqmlmoduleregistration.h>

#if __has_include(</home/csociety/CISociety/Qt/Plantlab/src/core/FileSystemController.py>)
#  include </home/csociety/CISociety/Qt/Plantlab/src/core/FileSystemController.py>
#endif


#if !defined(QT_STATIC)
#define Q_QMLTYPE_EXPORT Q_DECL_EXPORT
#else
#define Q_QMLTYPE_EXPORT
#endif
Q_QMLTYPE_EXPORT void qml_register_types_com_plantlab_controllers()
{
    QT_WARNING_PUSH QT_WARNING_DISABLE_DEPRECATED
    qmlRegisterTypesAndRevisions<FileSystemController>("com.plantlab.controllers", 1);
    QT_WARNING_POP
    qmlRegisterModule("com.plantlab.controllers", 1, 0);
}

static const QQmlModuleRegistration complantlabcontrollersRegistration("com.plantlab.controllers", qml_register_types_com_plantlab_controllers);
