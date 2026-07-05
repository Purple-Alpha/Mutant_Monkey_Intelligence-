// MMI boundary daemon skeleton — §17 Phase 4C (Go target runtime).
//
// Build (PC1 with Go installed):
//   go build -o mmi_boundary_daemon.exe .
//
// Run:
//   mmi_boundary_daemon.exe --policy policy_manifest.json --authority-manifest authority_manifest.json --evidence C:\mmi_m4_evidence\boundary --selftest
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"
)

type policyManifest struct {
	SchemaV          string `json:"schema_v"`
	AuthorityRoot    string `json:"authority_root"`
	ManifestHash     string `json:"manifest_hash"`
	PolicySignature  string `json:"policy_signature"`
	CustodyKeyID     string `json:"custody_key_id"`
	EntryCount       int    `json:"entry_count"`
}

type authorityManifest struct {
	ManifestHash string `json:"manifest_hash"`
}

type heartbeat struct {
	SchemaV          string `json:"schema_v"`
	Daemon           string `json:"daemon"`
	Armed            bool   `json:"armed"`
	LastHeartbeatUTC string `json:"last_heartbeat_utc"`
	ManifestHash     string `json:"manifest_hash"`
	Reason           string `json:"reason"`
}

func loadJSON(path string, out any) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, out)
}

func mayArm(policyPath, authorityManifestPath string) (bool, string, string) {
	var policy policyManifest
	if err := loadJSON(policyPath, &policy); err != nil {
		return false, "", fmt.Sprintf("policy_load_failed: %v", err)
	}
	var authority authorityManifest
	if err := loadJSON(authorityManifestPath, &authority); err != nil {
		return false, policy.ManifestHash, fmt.Sprintf("authority_manifest_load_failed: %v", err)
	}
	if policy.ManifestHash != authority.ManifestHash {
		return false, policy.ManifestHash, "manifest_hash_mismatch"
	}
	if policy.PolicySignature == "" {
		return false, policy.ManifestHash, "policy_signature_missing"
	}
	return true, policy.ManifestHash, "policy_manifest_ok"
}

func writeHeartbeat(evidenceDir string, hb heartbeat) error {
	path := evidenceDir + string(os.PathSeparator) + "daemon_heartbeat.json"
	data, err := json.MarshalIndent(hb, "", "  ")
	if err != nil {
		return err
	}
	data = append(data, '\n')
	return os.WriteFile(path, data, 0o644)
}

func appendEvent(evidenceDir, line string) error {
	f, err := os.OpenFile(evidenceDir+string(os.PathSeparator)+"daemon.jsonl", os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	defer f.Close()
	_, err = f.WriteString(line + "\n")
	return err
}

func main() {
	policy := flag.String("policy", "", "signed policy_manifest.json")
	authority := flag.String("authority-manifest", "", "authority_manifest.json")
	evidence := flag.String("evidence", "", "EVIDENCE_ROOT/boundary directory")
	selftest := flag.Bool("selftest", false, "run arm/refuse selftest")
	flag.Parse()

	if *selftest {
		if *policy == "" || *authority == "" || *evidence == "" {
			fmt.Fprintln(os.Stderr, "selftest requires --policy --authority-manifest --evidence")
			os.Exit(2)
		}
		ok, hash, reason := mayArm(*policy, *authority)
		_ = os.MkdirAll(*evidence, 0o755)
		hb := heartbeat{
			SchemaV:          "2026-07-04a",
			Daemon:           "mmi_boundary_daemon_go_skeleton",
			Armed:            ok,
			LastHeartbeatUTC: time.Now().UTC().Format(time.RFC3339Nano),
			ManifestHash:     hash,
			Reason:           reason,
		}
		if err := writeHeartbeat(*evidence, hb); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		event, _ := json.Marshal(map[string]any{
			"event": "selftest", "armed": ok, "reason": reason, "ts": hb.LastHeartbeatUTC,
		})
		_ = appendEvent(*evidence, string(event))
		if !ok {
			os.Exit(1)
		}
		fmt.Println("PASS")
		return
	}

	fmt.Fprintln(os.Stderr, "daemon skeleton: use --selftest for Phase 4C gate")
	os.Exit(2)
}
