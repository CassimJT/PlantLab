/****************************************************************************
** Generated QML type registration code
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <QtQml/qqml.h>
#include <QtQml/qqmlmoduleregistration.h>

#if __has_include(</home/csociety/CISociety/Qt/Plantlab/src/core/controllers/FileSystemController.py>)
#  include </home/csociety/CISociety/Qt/Plantlab/src/core/controllers/FileSystemController.py>
#endif


#if !defined(QT_STATIC)
#define Q_QMLTYPE_EXPORT Q_DECL_EXPORT
#else
#define Q_QMLTYPE_EXPORT
#endif
Q_QMLTYPE_EXPORT void qml_register_types_plantlab_models()
{
    QT_WARNING_PUSH QT_WARNING_DISABLE_DEPRECATED
    qmlRegisterTypesAndRevisions<FileSystemController>("plantlab.models", 1);
    QT_WARNING_POP
    qmlRegisterModule("plantlab.models", 1, 0);
}

static const QQmlModuleRegistration plantlabmodelsRegistration("plantlab.models", qml_register_types_plantlab_models);
