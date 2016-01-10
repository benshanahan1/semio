/****************************************************************************
** Meta object code from reading C++ file 'QtWrapperWidget.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.3.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../../Cashlab/Program/Semiology_20150120/Controller/QtWrapperWidget.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'QtWrapperWidget.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.3.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
struct qt_meta_stringdata_UI__QtWrapperWidget_t {
    QByteArrayData data[7];
    char stringdata[55];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_UI__QtWrapperWidget_t, stringdata) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_UI__QtWrapperWidget_t qt_meta_stringdata_UI__QtWrapperWidget = {
    {
QT_MOC_LITERAL(0, 0, 19),
QT_MOC_LITERAL(1, 20, 12),
QT_MOC_LITERAL(2, 33, 0),
QT_MOC_LITERAL(3, 34, 7),
QT_MOC_LITERAL(4, 42, 8),
QT_MOC_LITERAL(5, 51, 1),
QT_MOC_LITERAL(6, 53, 1)
    },
    "UI::QtWrapperWidget\0initializeGL\0\0"
    "paintGL\0resizeGL\0w\0h"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_UI__QtWrapperWidget[] = {

 // content:
       7,       // revision
       0,       // classname
       0,    0, // classinfo
       3,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    0,   29,    2, 0x0a /* Public */,
       3,    0,   30,    2, 0x0a /* Public */,
       4,    2,   31,    2, 0x0a /* Public */,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int, QMetaType::Int,    5,    6,

       0        // eod
};

void UI::QtWrapperWidget::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        QtWrapperWidget *_t = static_cast<QtWrapperWidget *>(_o);
        switch (_id) {
        case 0: _t->initializeGL(); break;
        case 1: _t->paintGL(); break;
        case 2: _t->resizeGL((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2]))); break;
        default: ;
        }
    }
}

const QMetaObject UI::QtWrapperWidget::staticMetaObject = {
    { &QGLWidget::staticMetaObject, qt_meta_stringdata_UI__QtWrapperWidget.data,
      qt_meta_data_UI__QtWrapperWidget,  qt_static_metacall, 0, 0}
};


const QMetaObject *UI::QtWrapperWidget::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *UI::QtWrapperWidget::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_UI__QtWrapperWidget.stringdata))
        return static_cast<void*>(const_cast< QtWrapperWidget*>(this));
    return QGLWidget::qt_metacast(_clname);
}

int UI::QtWrapperWidget::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QGLWidget::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 3)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 3;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 3)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 3;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
