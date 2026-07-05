/* MMI boundary minifilter — Phase 4D-b (§8).
 * Denies mutating IRPs under the configured authority volume path.
 * Policy FileId set sync via filter port is follow-up; path prefix closes T1 live.
 */
#include <fltKernel.h>

#define MMI_TAG 'miMM'
#define MMI_FILTER_PORT_NAME L"\\MmiBoundaryFilterPort"
#define MMI_DEFAULT_AUTHORITY L"\\Architectapp_clean"

PFLT_FILTER gFilterHandle = NULL;
UNICODE_STRING gAuthorityRoot = {0};
WCHAR gAuthorityRootBuffer[520];

static VOID MmiSetAuthorityRoot(_In_ PCUNICODE_STRING Root)
{
    USHORT bytes;

    if (Root == NULL || Root->Length == 0) {
        RtlInitUnicodeString(&gAuthorityRoot, MMI_DEFAULT_AUTHORITY);
        return;
    }

    bytes = min(Root->Length, (USHORT)(sizeof(gAuthorityRootBuffer) - sizeof(WCHAR)));
    RtlCopyMemory(gAuthorityRootBuffer, Root->Buffer, bytes);
    gAuthorityRootBuffer[bytes / sizeof(WCHAR)] = L'\0';
    gAuthorityRoot.Length = bytes;
    gAuthorityRoot.MaximumLength = (USHORT)sizeof(gAuthorityRootBuffer);
    gAuthorityRoot.Buffer = gAuthorityRootBuffer;
}

static NTSTATUS MmiLoadAuthorityRootFromRegistry(VOID)
{
    OBJECT_ATTRIBUTES objectAttributes;
    UNICODE_STRING keyPath;
    UNICODE_STRING valueName;
    HANDLE keyHandle = NULL;
    UCHAR buffer[sizeof(KEY_VALUE_PARTIAL_INFORMATION) + 520];
    PKEY_VALUE_PARTIAL_INFORMATION info;
    UNICODE_STRING value;
    ULONG infoLength;
    NTSTATUS status;

    RtlInitUnicodeString(&keyPath,
        L"\\Registry\\Machine\\System\\CurrentControlSet\\Services\\mmi_boundary\\Parameters");
    InitializeObjectAttributes(
        &objectAttributes,
        &keyPath,
        OBJ_CASE_INSENSITIVE | OBJ_KERNEL_HANDLE,
        NULL,
        NULL);

    status = ZwOpenKey(&keyHandle, KEY_READ, &objectAttributes);
    if (!NT_SUCCESS(status)) {
        MmiSetAuthorityRoot(NULL);
        return STATUS_SUCCESS;
    }

    RtlInitUnicodeString(&valueName, L"AuthorityRoot");
    info = (PKEY_VALUE_PARTIAL_INFORMATION)buffer;
    status = ZwQueryValueKey(
        keyHandle,
        &valueName,
        KeyValuePartialInformation,
        info,
        sizeof(buffer),
        &infoLength);
    ZwClose(keyHandle);

    if (!NT_SUCCESS(status) || info->Type != REG_SZ || info->DataLength < sizeof(WCHAR)) {
        MmiSetAuthorityRoot(NULL);
        return STATUS_SUCCESS;
    }

    value.Buffer = (PWCH)info->Data;
    value.Length = (USHORT)(info->DataLength - sizeof(WCHAR));
    value.MaximumLength = (USHORT)info->DataLength;
    MmiSetAuthorityRoot(&value);
    return STATUS_SUCCESS;
}

static BOOLEAN MmiNameUnderAuthority(_In_ PUNICODE_STRING Name)
{
    PWCH component;
    USHORT componentChars;
    USHORT nameChars;
    USHORT index;

    if (gAuthorityRoot.Length == 0 || Name == NULL || Name->Length == 0) {
        return FALSE;
    }

    component = gAuthorityRoot.Buffer;
    componentChars = gAuthorityRoot.Length / sizeof(WCHAR);
    if (componentChars == 0) {
        return FALSE;
    }
    if (component[0] == L'\\') {
        component++;
        componentChars--;
    }
    if (componentChars == 0) {
        return FALSE;
    }

    nameChars = Name->Length / sizeof(WCHAR);
    for (index = 0; index < nameChars; index++) {
        UNICODE_STRING segment;
        UNICODE_STRING componentString;
        WCHAR next;

        if (Name->Buffer[index] != L'\\') {
            continue;
        }

        if (index + 1 + componentChars > nameChars) {
            continue;
        }

        segment.Buffer = Name->Buffer + index + 1;
        segment.Length = (USHORT)(componentChars * sizeof(WCHAR));
        segment.MaximumLength = segment.Length;
        componentString.Buffer = component;
        componentString.Length = segment.Length;
        componentString.MaximumLength = segment.Length;
        if (RtlCompareUnicodeString(&segment, &componentString, TRUE) != 0) {
            continue;
        }

        next = (index + 1 + componentChars < nameChars)
            ? Name->Buffer[index + 1 + componentChars]
            : L'\0';
        if (next == L'\0' || next == L'\\') {
            return TRUE;
        }
    }

    return FALSE;
}

static BOOLEAN MmiCreateIsMutating(_Inout_ PFLT_CALLBACK_DATA Data)
{
    ACCESS_MASK access;
    ULONG disposition;

    if (Data->Iopb->MajorFunction != IRP_MJ_CREATE) {
        return TRUE;
    }

    access = Data->Iopb->Parameters.Create.SecurityContext->DesiredAccess;
    disposition = (Data->Iopb->Parameters.Create.Options >> 24) & 0xff;

    if (access & (DELETE | FILE_WRITE_DATA | FILE_APPEND_DATA | WRITE_DAC | WRITE_OWNER | GENERIC_WRITE)) {
        return TRUE;
    }

    if (disposition == FILE_SUPERSEDE ||
        disposition == FILE_OVERWRITE ||
        disposition == FILE_OVERWRITE_IF ||
        disposition == FILE_CREATE ||
        disposition == FILE_OPEN_IF) {
        return TRUE;
    }

    return FALSE;
}

static FLT_PREOP_CALLBACK_STATUS MmiCompleteDeny(_Inout_ PFLT_CALLBACK_DATA Data)
{
    Data->IoStatus.Status = STATUS_ACCESS_DENIED;
    Data->IoStatus.Information = 0;
    return FLT_PREOP_COMPLETE;
}

static NTSTATUS MmiInstanceSetup(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_SETUP_FLAGS Flags,
    _In_ DEVICE_TYPE VolumeDeviceType,
    _In_ FLT_FILESYSTEM_TYPE VolumeFilesystemType)
{
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(Flags);
    UNREFERENCED_PARAMETER(VolumeDeviceType);
    UNREFERENCED_PARAMETER(VolumeFilesystemType);
    return STATUS_SUCCESS;
}

static BOOLEAN MmiResolveNameInformation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _Outptr_ PFLT_FILE_NAME_INFORMATION *NameInfo)
{
    NTSTATUS status;

    status = FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
        NameInfo);
    if (NT_SUCCESS(status)) {
        return TRUE;
    }

    status = FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_OPENED | FLT_FILE_NAME_QUERY_DEFAULT,
        NameInfo);
    return NT_SUCCESS(status);
}

static FLT_PREOP_CALLBACK_STATUS MmiPreOperation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext,
    _In_ BOOLEAN checkCreateMutation)
{
    PFLT_FILE_NAME_INFORMATION nameInfo = NULL;
    NTSTATUS status;

    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);

    if (checkCreateMutation && !MmiCreateIsMutating(Data)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    if (!MmiResolveNameInformation(Data, &nameInfo)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    status = FltParseFileNameInformation(nameInfo);
    if (!NT_SUCCESS(status)) {
        FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }

    if (MmiNameUnderAuthority(&nameInfo->Name)) {
        FltReleaseFileNameInformation(nameInfo);
        return MmiCompleteDeny(Data);
    }

    FltReleaseFileNameInformation(nameInfo);
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

static FLT_PREOP_CALLBACK_STATUS MmiPreCreate(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext)
{
    return MmiPreOperation(Data, FltObjects, CompletionContext, TRUE);
}

static FLT_PREOP_CALLBACK_STATUS MmiPreWrite(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext)
{
    return MmiPreOperation(Data, FltObjects, CompletionContext, FALSE);
}

static FLT_PREOP_CALLBACK_STATUS MmiPreSetInformation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext)
{
    return MmiPreOperation(Data, FltObjects, CompletionContext, FALSE);
}

static FLT_PREOP_CALLBACK_STATUS MmiPreSetSecurity(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext)
{
    return MmiPreOperation(Data, FltObjects, CompletionContext, FALSE);
}

static const FLT_OPERATION_REGISTRATION Callbacks[] = {
    { IRP_MJ_CREATE, 0, MmiPreCreate, NULL },
    { IRP_MJ_WRITE, 0, MmiPreWrite, NULL },
    { IRP_MJ_SET_INFORMATION, 0, MmiPreSetInformation, NULL },
    { IRP_MJ_SET_SECURITY, 0, MmiPreSetSecurity, NULL },
    { IRP_MJ_OPERATION_END }
};

static NTSTATUS MmiUnload(_In_ FLT_FILTER_UNLOAD_FLAGS Flags)
{
    UNREFERENCED_PARAMETER(Flags);
    FltUnregisterFilter(gFilterHandle);
    gFilterHandle = NULL;
    return STATUS_SUCCESS;
}

static const FLT_REGISTRATION FilterRegistration = {
    sizeof(FLT_REGISTRATION),
    FLT_REGISTRATION_VERSION,
    0,
    NULL,
    Callbacks,
    MmiUnload,
    MmiInstanceSetup,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
};

NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath)
{
    NTSTATUS status;

    UNREFERENCED_PARAMETER(RegistryPath);

    status = FltRegisterFilter(DriverObject, &FilterRegistration, &gFilterHandle);
    if (!NT_SUCCESS(status)) {
        return status;
    }

    MmiLoadAuthorityRootFromRegistry();

    status = FltStartFiltering(gFilterHandle);
    if (!NT_SUCCESS(status)) {
        FltUnregisterFilter(gFilterHandle);
        gFilterHandle = NULL;
        return status;
    }

    return STATUS_SUCCESS;
}
