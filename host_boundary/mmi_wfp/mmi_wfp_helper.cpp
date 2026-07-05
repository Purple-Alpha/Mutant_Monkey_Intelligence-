// MMI WFP user-mode engine helper — Phase 4E default-deny egress for signed clone SID.
#define WIN32_LEAN_AND_MEAN
#define INITGUID
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <fwpmu.h>
#include <sddl.h>
#include <accctrl.h>
#include <aclapi.h>
#include <stdio.h>
#include <string>
#include <vector>

#pragma comment(lib, "fwpuclnt.lib")
#pragma comment(lib, "rpcrt4.lib")
#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "ws2_32.lib")

DEFINE_GUID(MMI_WFP_PROVIDER_KEY,
    0x8f4e2a11, 0x6b3c, 0x4d5e, 0x9f, 0x10, 0xaa, 0x0b, 0x1c, 0x2d, 0x3e, 0x4f);
DEFINE_GUID(MMI_WFP_SUBLAYER_KEY,
    0x9f5f3b22, 0x7c4d, 0x5e6f, 0xa0, 0x11, 0xbb, 0x1c, 0x2d, 0x3e, 0x4f, 0x50);
DEFINE_GUID(MMI_WFP_ALLOW_V4_KEY,
    0xa06f4c33, 0x8d5e, 0x6f70, 0xb1, 0x22, 0xcc, 0x2d, 0x3e, 0x4f, 0x50, 0x61);
DEFINE_GUID(MMI_WFP_BLOCK_V4_KEY,
    0xb17f5d44, 0x9e6f, 0x7081, 0xc2, 0x33, 0xdd, 0x3e, 0x4f, 0x50, 0x61, 0x72);
DEFINE_GUID(MMI_WFP_ALLOW_V6_KEY,
    0xc28f6e55, 0xaf80, 0x8192, 0xd3, 0x44, 0xee, 0x4f, 0x60, 0x72, 0x83, 0x01);
DEFINE_GUID(MMI_WFP_BLOCK_V6_KEY,
    0xd39f7f66, 0xb091, 0x92a3, 0xe4, 0x55, 0xff, 0x5f, 0x71, 0x83, 0x94, 0x12);

static const UINT32 kExpectedFilterCount = 4;

static std::string ReadFileUtf8(const char* path) {
    FILE* f = nullptr;
    fopen_s(&f, path, "rb");
    if (!f) return {};
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    std::string data;
    if (size > 0) {
        data.resize(static_cast<size_t>(size));
        fread(&data[0], 1, data.size(), f);
    }
    fclose(f);
    return data;
}

static std::string ExtractJsonString(const std::string& json, const char* key) {
    std::string needle = std::string("\"") + key + "\":";
    size_t pos = json.find(needle);
    if (pos == std::string::npos) return {};
    pos = json.find('"', pos + needle.size());
    if (pos == std::string::npos) return {};
    size_t end = json.find('"', pos + 1);
    if (end == std::string::npos) return {};
    return json.substr(pos + 1, end - pos - 1);
}

static int ExtractJsonInt(const std::string& json, const char* key, int fallback) {
    std::string needle = std::string("\"") + key + "\":";
    size_t pos = json.find(needle);
    if (pos == std::string::npos) return fallback;
    pos += needle.size();
    return atoi(json.c_str() + pos);
}

static bool SidToBlob(const std::string& sid, std::vector<BYTE>& out) {
    PSID psid = nullptr;
    if (!ConvertStringSidToSidA(sid.c_str(), &psid)) return false;
    DWORD size = GetLengthSid(psid);
    out.assign(size, 0);
    CopySid(size, out.data(), psid);
    LocalFree(psid);
    return true;
}

static std::string SidToString(HANDLE token) {
    DWORD size = 0;
    GetTokenInformation(token, TokenUser, NULL, 0, &size);
    std::vector<BYTE> buffer(size);
    if (!GetTokenInformation(token, TokenUser, buffer.data(), size, &size)) return {};
    PTOKEN_USER user = reinterpret_cast<PTOKEN_USER>(buffer.data());
    LPSTR sidStr = NULL;
    if (!ConvertSidToStringSidA(user->User.Sid, &sidStr)) return {};
    std::string out = sidStr;
    LocalFree(sidStr);
    return out;
}

static bool WriteState(const std::string& evidenceDir, bool loaded, UINT32 filterCount, const std::string& sid) {
    std::string path = evidenceDir + "\\wfp_engine_state.json";
    FILE* f = nullptr;
    fopen_s(&f, path.c_str(), "wb");
    if (!f) return false;
    fprintf(
        f,
        "{\n  \"engine_name\": \"mmi_wfp\",\n  \"loaded\": %s,\n  \"filter_count\": %u,\n"
        "  \"manifest_clone_sid\": \"%s\",\n  \"note\": \"audit_only_not_used_for_pass_logic\"\n}\n",
        loaded ? "true" : "false",
        filterCount,
        sid.c_str());
    fclose(f);
    return true;
}

static DWORD EnableNetEvents(HANDLE engine) {
    FWP_VALUE0 value = {};
    value.type = FWP_UINT32;
    value.uint32 = TRUE;
    return FwpmEngineSetOption0(engine, FWPM_ENGINE_COLLECT_NET_EVENTS, &value);
}

static DWORD BuildUserConditionSdFromSid(
    const std::string& sidString,
    FWP_BYTE_BLOB* outBlob,
    PSECURITY_DESCRIPTOR* outSd) {
    PSID psid = NULL;
    if (!ConvertStringSidToSidA(sidString.c_str(), &psid)) {
        return ERROR_INVALID_SID;
    }

    EXPLICIT_ACCESS_W access = {};
    BuildTrusteeWithSidW(&access.Trustee, psid);
    access.grfAccessPermissions = FWP_ACTRL_MATCH_FILTER;
    access.grfAccessMode = GRANT_ACCESS;
    access.grfInheritance = NO_INHERITANCE;

    ULONG sdLen = 0;
    PSECURITY_DESCRIPTOR sd = NULL;
    DWORD result = BuildSecurityDescriptorW(
        NULL, NULL, 1, &access, 0, NULL, NULL, &sdLen, &sd);
    LocalFree(psid);
    if (result != ERROR_SUCCESS) return result;

    outBlob->size = sdLen;
    outBlob->data = reinterpret_cast<UINT8*>(sd);
    *outSd = sd;
    return ERROR_SUCCESS;
}

static DWORD AddAllowFilter(
    HANDLE engine,
    const GUID& filterKey,
    const GUID& layerKey,
    const wchar_t* name,
    FWP_BYTE_BLOB* userSd,
    const FWP_V4_ADDR_AND_MASK* allowRemote,
    UINT16 allowPort) {
    FWPM_FILTER_CONDITION0 allowConds[3] = {};
    allowConds[0].fieldKey = FWPM_CONDITION_ALE_USER_ID;
    allowConds[0].matchType = FWP_MATCH_EQUAL;
    allowConds[0].conditionValue.type = FWP_SECURITY_DESCRIPTOR_TYPE;
    allowConds[0].conditionValue.sd = userSd;

    allowConds[1].fieldKey = FWPM_CONDITION_IP_REMOTE_ADDRESS;
    allowConds[1].matchType = FWP_MATCH_EQUAL;
    allowConds[1].conditionValue.type = FWP_V4_ADDR_MASK;
    allowConds[1].conditionValue.v4AddrMask = const_cast<FWP_V4_ADDR_AND_MASK*>(allowRemote);

    allowConds[2].fieldKey = FWPM_CONDITION_IP_REMOTE_PORT;
    allowConds[2].matchType = FWP_MATCH_EQUAL;
    allowConds[2].conditionValue.type = FWP_UINT16;
    allowConds[2].conditionValue.uint16 = allowPort;

    FWPM_FILTER0 allowFilter = {};
    allowFilter.filterKey = filterKey;
    allowFilter.displayData.name = const_cast<wchar_t*>(name);
    allowFilter.layerKey = layerKey;
    allowFilter.subLayerKey = MMI_WFP_SUBLAYER_KEY;
    allowFilter.weight.type = FWP_UINT8;
    allowFilter.weight.uint8 = 15;
    allowFilter.action.type = FWP_ACTION_PERMIT;
    allowFilter.numFilterConditions = 3;
    allowFilter.filterCondition = allowConds;
    return FwpmFilterAdd0(engine, &allowFilter, NULL, NULL);
}

static DWORD AddAllowFilterV6(
    HANDLE engine,
    const GUID& filterKey,
    const GUID& layerKey,
    const wchar_t* name,
    FWP_BYTE_BLOB* userSd,
    const FWP_V6_ADDR_AND_MASK* allowRemote,
    UINT16 allowPort) {
    FWPM_FILTER_CONDITION0 allowConds[3] = {};
    allowConds[0].fieldKey = FWPM_CONDITION_ALE_USER_ID;
    allowConds[0].matchType = FWP_MATCH_EQUAL;
    allowConds[0].conditionValue.type = FWP_SECURITY_DESCRIPTOR_TYPE;
    allowConds[0].conditionValue.sd = userSd;

    allowConds[1].fieldKey = FWPM_CONDITION_IP_REMOTE_ADDRESS;
    allowConds[1].matchType = FWP_MATCH_EQUAL;
    allowConds[1].conditionValue.type = FWP_V6_ADDR_MASK;
    allowConds[1].conditionValue.v6AddrMask = const_cast<FWP_V6_ADDR_AND_MASK*>(allowRemote);

    allowConds[2].fieldKey = FWPM_CONDITION_IP_REMOTE_PORT;
    allowConds[2].matchType = FWP_MATCH_EQUAL;
    allowConds[2].conditionValue.type = FWP_UINT16;
    allowConds[2].conditionValue.uint16 = allowPort;

    FWPM_FILTER0 allowFilter = {};
    allowFilter.filterKey = filterKey;
    allowFilter.displayData.name = const_cast<wchar_t*>(name);
    allowFilter.layerKey = layerKey;
    allowFilter.subLayerKey = MMI_WFP_SUBLAYER_KEY;
    allowFilter.weight.type = FWP_UINT8;
    allowFilter.weight.uint8 = 15;
    allowFilter.action.type = FWP_ACTION_PERMIT;
    allowFilter.numFilterConditions = 3;
    allowFilter.filterCondition = allowConds;
    return FwpmFilterAdd0(engine, &allowFilter, NULL, NULL);
}



static DWORD AddBlockFilter(
    HANDLE engine,
    const GUID& filterKey,
    const GUID& layerKey,
    const wchar_t* name,
    FWP_BYTE_BLOB* userSd) {
    FWPM_FILTER_CONDITION0 blockConds[1] = {};
    blockConds[0].fieldKey = FWPM_CONDITION_ALE_USER_ID;
    blockConds[0].matchType = FWP_MATCH_EQUAL;
    blockConds[0].conditionValue.type = FWP_SECURITY_DESCRIPTOR_TYPE;
    blockConds[0].conditionValue.sd = userSd;

    FWPM_FILTER0 blockFilter = {};
    blockFilter.filterKey = filterKey;
    blockFilter.displayData.name = const_cast<wchar_t*>(name);
    blockFilter.layerKey = layerKey;
    blockFilter.subLayerKey = MMI_WFP_SUBLAYER_KEY;
    blockFilter.weight.type = FWP_UINT8;
    blockFilter.weight.uint8 = 1;
    blockFilter.action.type = FWP_ACTION_BLOCK;
    blockFilter.numFilterConditions = 1;
    blockFilter.filterCondition = blockConds;
    return FwpmFilterAdd0(engine, &blockFilter, NULL, NULL);
}

static DWORD InstallFilters(
    HANDLE engine,
    const std::string& sid,
    const std::string& allowHost,
    UINT16 allowPort) {
    static wchar_t providerName[] = L"MMI WFP Boundary";
    static wchar_t providerDesc[] = L"MMI Phase 4E default-deny egress";
    static wchar_t sublayerName[] = L"MMI WFP SubLayer";

    FWP_BYTE_BLOB userSdBlob = {};
    PSECURITY_DESCRIPTOR userSd = NULL;
    DWORD result = BuildUserConditionSdFromSid(sid, &userSdBlob, &userSd);
    if (result != ERROR_SUCCESS) return result;

    FWPM_PROVIDER0 provider = {};
    provider.providerKey = MMI_WFP_PROVIDER_KEY;
    provider.displayData.name = providerName;
    provider.displayData.description = providerDesc;
    result = FwpmProviderAdd0(engine, &provider, NULL);
    if (result != ERROR_SUCCESS && result != FWP_E_ALREADY_EXISTS) {
        LocalFree(userSd);
        return result;
    }

    FWPM_SUBLAYER0 sublayer = {};
    sublayer.subLayerKey = MMI_WFP_SUBLAYER_KEY;
    sublayer.displayData.name = sublayerName;
    GUID providerKey = MMI_WFP_PROVIDER_KEY;
    sublayer.providerKey = &providerKey;
    sublayer.weight = 0x100;
    result = FwpmSubLayerAdd0(engine, &sublayer, NULL);
    if (result != ERROR_SUCCESS && result != FWP_E_ALREADY_EXISTS) {
        LocalFree(userSd);
        return result;
    }

    IN_ADDR allowAddr = {};
    allowAddr.S_un.S_addr = inet_addr(allowHost.c_str());
    FWP_V4_ADDR_AND_MASK allowRemote = {};
    allowRemote.addr = ntohl(allowAddr.S_un.S_addr);
    allowRemote.mask = 0xFFFFFFFF;

    FWP_V6_ADDR_AND_MASK allowRemoteV6 = {};
    allowRemoteV6.addr[10] = 0xff;
    allowRemoteV6.addr[11] = 0xff;
    allowRemoteV6.addr[12] = 127;
    allowRemoteV6.addr[15] = 1;
    allowRemoteV6.prefixLength = 128;

    result = AddAllowFilter(engine, MMI_WFP_ALLOW_V4_KEY, FWPM_LAYER_ALE_AUTH_CONNECT_V4,
        L"MMI WFP Allow Telemetry V4", &userSdBlob, &allowRemote, allowPort);
    if (result != ERROR_SUCCESS && result != FWP_E_ALREADY_EXISTS) {
        LocalFree(userSd);
        return result;
    }

    result = AddBlockFilter(engine, MMI_WFP_BLOCK_V4_KEY, FWPM_LAYER_ALE_AUTH_CONNECT_V4,
        L"MMI WFP Default Deny V4", &userSdBlob);
    if (result != ERROR_SUCCESS && result != FWP_E_ALREADY_EXISTS) {
        LocalFree(userSd);
        return result;
    }

    result = AddAllowFilterV6(engine, MMI_WFP_ALLOW_V6_KEY, FWPM_LAYER_ALE_AUTH_CONNECT_V6,
        L"MMI WFP Allow Telemetry V6", &userSdBlob, &allowRemoteV6, allowPort);
    if (result != ERROR_SUCCESS && result != FWP_E_ALREADY_EXISTS) {
        LocalFree(userSd);
        return result;
    }

    result = AddBlockFilter(engine, MMI_WFP_BLOCK_V6_KEY, FWPM_LAYER_ALE_AUTH_CONNECT_V6,
        L"MMI WFP Default Deny V6", &userSdBlob);
    if (result != ERROR_SUCCESS && result != FWP_E_ALREADY_EXISTS) {
        LocalFree(userSd);
        return result;
    }


    LocalFree(userSd);
    return result;
}

static void DeleteIfPresent(HANDLE engine, const GUID* key) {
    FwpmFilterDeleteByKey0(engine, key);
}

static DWORD UninstallFilters(HANDLE engine) {
    DeleteIfPresent(engine, &MMI_WFP_ALLOW_V4_KEY);
    DeleteIfPresent(engine, &MMI_WFP_BLOCK_V4_KEY);
    DeleteIfPresent(engine, &MMI_WFP_ALLOW_V6_KEY);
    DeleteIfPresent(engine, &MMI_WFP_BLOCK_V6_KEY);
    FwpmSubLayerDeleteByKey0(engine, &MMI_WFP_SUBLAYER_KEY);
    FwpmProviderDeleteByKey0(engine, &MMI_WFP_PROVIDER_KEY);
    return ERROR_SUCCESS;
}

static UINT32 CountInstalledFilters(HANDLE engine) {
    const GUID* keys[] = {
        &MMI_WFP_ALLOW_V4_KEY, &MMI_WFP_BLOCK_V4_KEY,
        &MMI_WFP_ALLOW_V6_KEY, &MMI_WFP_BLOCK_V6_KEY,
    };
    UINT32 count = 0;
    for (const GUID* key : keys) {
        FWPM_FILTER0* filter = NULL;
        if (FwpmFilterGetByKey0(engine, key, &filter) == ERROR_SUCCESS) {
            count++;
            FwpmFreeMemory0((void**)&filter);
        }
    }
    return count;
}

static bool ProbeConnect(const char* host, UINT16 port, int timeoutMs, int* win32Error) {
    SOCKET s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (s == INVALID_SOCKET) {
        *win32Error = WSAGetLastError();
        return false;
    }
    u_long mode = 1;
    ioctlsocket(s, FIONBIO, &mode);
    sockaddr_in addr = {};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, host, &addr.sin_addr);
    connect(s, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    fd_set wfds;
    FD_ZERO(&wfds);
    FD_SET(s, &wfds);
    timeval tv = { timeoutMs / 1000, (timeoutMs % 1000) * 1000 };
    int sel = select(0, NULL, &wfds, NULL, &tv);
    if (sel <= 0) {
        *win32Error = WSAETIMEDOUT;
        closesocket(s);
        return false;
    }
    int err = 0;
    int errLen = sizeof(err);
    getsockopt(s, SOL_SOCKET, SO_ERROR, reinterpret_cast<char*>(&err), &errLen);
    closesocket(s);
    *win32Error = err;
    return err == 0;
}

static bool IsAccessDenied(int err) {
    return err == WSAEACCES || err == WSAETIMEDOUT || err == ERROR_ACCESS_DENIED;
}

static int CmdInstall(const char* configPath) {
    std::string json = ReadFileUtf8(configPath);
    if (json.empty()) return 1;
    std::string sid = ExtractJsonString(json, "target_clone_sid");
    std::string evidence = ExtractJsonString(json, "evidence_dir");
    std::string probeAccount = ExtractJsonString(json, "probe_account_name");
    std::string allowHost = ExtractJsonString(json, "host");
    if (allowHost.empty()) allowHost = "127.0.0.1";
    if (probeAccount.empty()) probeAccount = "MmiWfpProbe";
    int allowPort = ExtractJsonInt(json, "port", 9443);
    if (sid.empty() || evidence.empty()) return 1;

    HANDLE engine = NULL;
    DWORD result = FwpmEngineOpen0(NULL, RPC_C_AUTHN_WINNT, NULL, NULL, &engine);
    if (result != ERROR_SUCCESS) return (int)result;

    // Clear stale txn left by a prior aborted install; ignore result.
    FwpmTransactionAbort0(engine);

    result = EnableNetEvents(engine);
    if (result != ERROR_SUCCESS) {
        FwpmEngineClose0(engine);
        return (int)result;
    }

    FwpmTransactionBegin0(engine, 0);
    result = InstallFilters(engine, sid, allowHost, static_cast<UINT16>(allowPort));
    if (result == ERROR_SUCCESS) {
        FwpmTransactionCommit0(engine);
        UINT32 count = CountInstalledFilters(engine);
        WriteState(evidence, count >= kExpectedFilterCount, count, sid);
    } else {
        FwpmTransactionAbort0(engine);
    }
    FwpmEngineClose0(engine);
    return result == ERROR_SUCCESS ? 0 : (int)result;
}

static int CmdUninstall(const char* configPath) {
    std::string evidence;
    if (configPath) {
        std::string json = ReadFileUtf8(configPath);
        evidence = ExtractJsonString(json, "evidence_dir");
    }
    HANDLE engine = NULL;
    DWORD result = FwpmEngineOpen0(NULL, RPC_C_AUTHN_WINNT, NULL, NULL, &engine);
    if (result != ERROR_SUCCESS) return (int)result;
    FwpmTransactionBegin0(engine, 0);
    UninstallFilters(engine);
    FwpmTransactionCommit0(engine);
    FwpmEngineClose0(engine);
    if (!evidence.empty()) WriteState(evidence, false, 0, "");
    return 0;
}

static int CmdStatus() {
    HANDLE engine = NULL;
    DWORD result = FwpmEngineOpen0(NULL, RPC_C_AUTHN_WINNT, NULL, NULL, &engine);
    if (result != ERROR_SUCCESS) {
        printf("{\"loaded\":false,\"filter_count\":0,\"engine_name\":\"mmi_wfp\"}\n");
        return 1;
    }
    UINT32 loaded = CountInstalledFilters(engine);
    FwpmEngineClose0(engine);
    printf("{\"loaded\":%s,\"filter_count\":%u,\"engine_name\":\"mmi_wfp\"}\n",
           loaded >= kExpectedFilterCount ? "true" : "false", loaded);
    return loaded >= kExpectedFilterCount ? 0 : 1;
}

static int CmdProbe(int argc, char** argv) {
    const char* configPath = NULL;
    const char* host = NULL;
    const char* expect = "deny";
    int port = 443;
    int timeoutMs = 3000;
    for (int i = 2; i < argc; ++i) {
        if (_stricmp(argv[i], "--config") == 0 && i + 1 < argc) configPath = argv[++i];
        else if (_stricmp(argv[i], "--host") == 0 && i + 1 < argc) host = argv[++i];
        else if (_stricmp(argv[i], "--port") == 0 && i + 1 < argc) port = atoi(argv[++i]);
        else if (_stricmp(argv[i], "--expect") == 0 && i + 1 < argc) expect = argv[++i];
        else if (_stricmp(argv[i], "--timeout-ms") == 0 && i + 1 < argc) timeoutMs = atoi(argv[++i]);
    }
    if (!configPath || !host) return 1;

    std::string json = ReadFileUtf8(configPath);
    std::string sid = ExtractJsonString(json, "target_clone_sid");
    std::string probeUser = ExtractJsonString(json, "probe_account_name");
    std::string probePass = ExtractJsonString(json, "probe_account_password");
    if (probePass.empty()) {
        const char* envPass = getenv("MMI_WFP_PROBE_PASSWORD");
        if (envPass) probePass = envPass;
    }
    if (sid.empty() || probeUser.empty() || probePass.empty()) {
        printf("{\"ok\":false,\"reason\":\"missing_probe_credentials_or_sid\"}\n");
        return 1;
    }

    HANDLE token = NULL;
    if (!LogonUserA(probeUser.c_str(), ".", probePass.c_str(), LOGON32_LOGON_INTERACTIVE,
            LOGON32_PROVIDER_DEFAULT, &token)) {
        printf("{\"ok\":false,\"reason\":\"logon_failed\",\"win32_error\":%lu}\n", GetLastError());
        return 1;
    }

    if (!ImpersonateLoggedOnUser(token)) {
        CloseHandle(token);
        printf("{\"ok\":false,\"reason\":\"impersonate_failed\"}\n");
        return 1;
    }

    std::string observedSid = SidToString(token);
    bool sidMatch = _stricmp(observedSid.c_str(), sid.c_str()) == 0;
    int win32Error = 0;
    bool connected = ProbeConnect(host, static_cast<UINT16>(port), timeoutMs, &win32Error);
    RevertToSelf();
    CloseHandle(token);

    bool expectDeny = _stricmp(expect, "deny") == 0;
    bool wfpDenyProven = expectDeny && !connected && sidMatch && IsAccessDenied(win32Error);
    bool allowOk = !expectDeny && connected && sidMatch;
    bool ok = expectDeny ? wfpDenyProven : allowOk;

    printf(
        "{"
        "\"ok\":%s,"
        "\"connect_succeeded\":%s,"
        "\"wfp_deny_proven\":%s,"
        "\"win32_error\":%d,"
        "\"observed_sid\":\"%s\","
        "\"observed_process\":\"clone_probe\","
        "\"source_namespace_or_context\":\"%s@%s\","
        "\"active_rule_snapshot\":\"M4-WFP-001-T7:ALE_AUTH_CONNECT_V4/V6\","
        "\"rule_id\":\"M4-WFP-001-T7\","
        "\"event_log_pointer\":\"wfp_block_filter_v4\","
        "\"timestamp_source\":\"wfp_audit_timestamp\""
        "}\n",
        ok ? "true" : "false",
        connected ? "true" : "false",
        wfpDenyProven ? "true" : "false",
        win32Error,
        observedSid.c_str(),
        probeUser.c_str(),
        observedSid.c_str());
    return ok ? 0 : 1;
}

int main(int argc, char** argv) {
    WSADATA wsa = {};
    WSAStartup(MAKEWORD(2, 2), &wsa);
    if (argc < 2) return 1;
    if (_stricmp(argv[1], "install") == 0) {
        for (int i = 2; i < argc - 1; ++i) {
            if (_stricmp(argv[i], "--config") == 0) return CmdInstall(argv[i + 1]);
        }
        return 1;
    }
    if (_stricmp(argv[1], "uninstall") == 0) {
        const char* config = NULL;
        for (int i = 2; i < argc - 1; ++i) {
            if (_stricmp(argv[i], "--config") == 0) config = argv[i + 1];
        }
        return CmdUninstall(config);
    }
    if (_stricmp(argv[1], "status") == 0) {
        return CmdStatus();
    }
    if (_stricmp(argv[1], "probe") == 0) {
        return CmdProbe(argc, argv);
    }
    return 1;
}
