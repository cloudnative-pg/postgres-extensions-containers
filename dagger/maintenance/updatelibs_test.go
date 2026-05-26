package main

import (
	"strings"
	"testing"
)

func TestLibsRegex(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		wantLib  string
		wantHash string
		match    bool
	}{
		{
			name:     "standard line with MD5Sum",
			input:    "'http://deb.debian.org/debian/pool/main/liba/libaec/libaec0_1.0.6-1+b1_amd64.deb' libaec0_1.0.6-1+b1_amd64.deb 22052 MD5Sum:42611bf8032dad2d74c26d8dc084d322",
			wantLib:  "libaec0_1.0.6-1+b1_amd64.deb",
			wantHash: "MD5Sum:42611bf8032dad2d74c26d8dc084d322",
			match:    true,
		},
		{
			name:     "line without MD5Sum",
			input:    "'http://deb.debian.org/debian/pool/main/libn/libnss3/libnss3_3.87.1-1+deb12u1_amd64.deb' libnss3_3.87.1-1+deb12u1_amd64.deb 1378920",
			wantLib:  "libnss3_3.87.1-1+deb12u1_amd64.deb",
			wantHash: "",
			match:    true,
		},
		{
			name:     "epoch in version (URL-encoded colon)",
			input:    "'http://deb.debian.org/debian/pool/main/liba/libarmadillo/libarmadillo11_1%3a11.4.2+dfsg-1_amd64.deb' libarmadillo11_1%3a11.4.2+dfsg-1_amd64.deb 11340 MD5Sum:0ec736fe1888c654c32c3812add9d61d",
			wantLib:  "libarmadillo11_1%3a11.4.2+dfsg-1_amd64.deb",
			wantHash: "MD5Sum:0ec736fe1888c654c32c3812add9d61d",
			match:    true,
		},
		{
			name:     "trailing whitespace after MD5Sum",
			input:    "'http://example.com/libfoo_1.0_amd64.deb' libfoo_1.0_amd64.deb 4096 MD5Sum:abc123   ",
			wantLib:  "libfoo_1.0_amd64.deb",
			wantHash: "MD5Sum:abc123",
			match:    true,
		},
		{
			name:     "trailing whitespace without MD5Sum",
			input:    "'http://example.com/libfoo_1.0_amd64.deb' libfoo_1.0_amd64.deb 4096   ",
			wantLib:  "libfoo_1.0_amd64.deb",
			wantHash: "",
			match:    true,
		},
		{
			name:  "non-lib package is excluded",
			input: "'http://deb.debian.org/debian/pool/main/p/proj/proj-data_9.1.1-1_all.deb' proj-data_9.1.1-1_all.deb 7891012 MD5Sum:deadbeef",
			match: false,
		},
		{
			name:  "non-deb file is excluded",
			input: "'http://example.com/libfoo_1.0.tar.gz' libfoo_1.0.tar.gz 4096 MD5Sum:abc123",
			match: false,
		},
		{
			name:  "empty line",
			input: "",
			match: false,
		},
		{
			name:  "noise line from apt-get",
			input: "Reading package lists...",
			match: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			matches := libsRegex.FindStringSubmatch(tt.input)
			if !tt.match {
				if matches != nil {
					t.Errorf("expected no match, got %v", matches)
				}
				return
			}
			if matches == nil {
				t.Fatal("expected a match, got nil")
			}
			if matches[1] != tt.wantLib {
				t.Errorf("library name: got %q, want %q", matches[1], tt.wantLib)
			}
			if matches[2] != tt.wantHash {
				t.Errorf("MD5Sum: got %q, want %q", matches[2], tt.wantHash)
			}
		})
	}
}

func TestLibsRegexMultiline(t *testing.T) {
	input := `Reading package lists...
Building dependency tree...
'http://deb.debian.org/debian/pool/main/liba/libaec/libaec0_1.0.6-1+b1_amd64.deb' libaec0_1.0.6-1+b1_amd64.deb 22052 MD5Sum:42611bf8032dad2d74c26d8dc084d322
'http://deb.debian.org/debian/pool/main/libn/libnss3/libnss3_3.87.1-1_amd64.deb' libnss3_3.87.1-1_amd64.deb 1378920
'http://deb.debian.org/debian/pool/main/p/proj/proj-data_9.1.1-1_all.deb' proj-data_9.1.1-1_all.deb 7891012 MD5Sum:deadbeef`

	matches := libsRegex.FindAllStringSubmatch(input, -1)
	if len(matches) != 2 {
		t.Fatalf("expected 2 matches, got %d", len(matches))
	}

	if matches[0][1] != "libaec0_1.0.6-1+b1_amd64.deb" {
		t.Errorf("match 0 lib: got %q", matches[0][1])
	}
	if matches[0][2] != "MD5Sum:42611bf8032dad2d74c26d8dc084d322" {
		t.Errorf("match 0 hash: got %q", matches[0][2])
	}

	if matches[1][1] != "libnss3_3.87.1-1_amd64.deb" {
		t.Errorf("match 1 lib: got %q", matches[1][1])
	}
	if matches[1][2] != "" {
		t.Errorf("match 1 hash: expected empty, got %q", matches[1][2])
	}
}

func TestBuildResultFromMatches(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  string
	}{
		{
			name:  "with MD5Sum",
			input: "'http://example.com/libfoo_1.0_amd64.deb' libfoo_1.0_amd64.deb 4096 MD5Sum:abc123",
			want:  "libfoo_1.0_amd64.deb MD5Sum:abc123\n",
		},
		{
			name:  "without MD5Sum",
			input: "'http://example.com/libfoo_1.0_amd64.deb' libfoo_1.0_amd64.deb 4096",
			want:  "libfoo_1.0_amd64.deb\n",
		},
		{
			name: "mixed lines",
			input: `'http://example.com/libfoo_1.0_amd64.deb' libfoo_1.0_amd64.deb 4096 MD5Sum:abc123
'http://example.com/libbar_2.0_amd64.deb' libbar_2.0_amd64.deb 8192`,
			want: "libfoo_1.0_amd64.deb MD5Sum:abc123\nlibbar_2.0_amd64.deb\n",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			matches := libsRegex.FindAllStringSubmatch(tt.input, -1)
			var result string
			for _, m := range matches {
				line := strings.Join(m[1:], " ")
				result += strings.TrimSpace(line) + "\n"
			}
			if result != tt.want {
				t.Errorf("got %q, want %q", result, tt.want)
			}
		})
	}
}
