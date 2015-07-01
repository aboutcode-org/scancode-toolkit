/*
 * Command line utility to exercise the QEMU I/O path.
 *
 * Copyright (C) 2009 Red Hat, Inc.
 * Copyright (c) 2003-2005 Silicon Graphics, Inc.
 *
 * This work is licensed under the terms of the GNU GPL, version 2 or later.
	int pattern = 0, pattern_offset = 0, pattern_count = 0;

	while ((c = getopt(argc, argv, "bCl:pP:qs:v")) != EOF) {
		switch (c) {
		case 'b':
			bflag = 1;
	int Pflag = 0;

	while ((c = getopt(argc, argv, "CP:qv")) != EOF) {
		switch (c) {
		case 'C':
			Cflag = 1;
	int pattern = 0xcd;

	while ((c = getopt(argc, argv, "bCpP:q")) != EOF) {
		switch (c) {
		case 'b':
			bflag = 1;
	QEMUIOVector qiov;

	while ((c = getopt(argc, argv, "CqP:")) != EOF) {
		switch (c) {
		case 'C':
			Cflag = 1;
	BlockRequest *reqs;

	while ((c = getopt(argc, argv, "CqP:")) != EOF) {
		switch (c) {
		case 'C':
			Cflag = 1;
	BlockDriverAIOCB *acb;

	while ((c = getopt(argc, argv, "CP:qv")) != EOF) {
		switch (c) {
		case 'C':
			ctx->Cflag = 1;
	BlockDriverAIOCB *acb;

	while ((c = getopt(argc, argv, "CqP:")) != EOF) {
		switch (c) {
		case 'C':
			ctx->Cflag = 1;
	int count;

	while ((c = getopt(argc, argv, "Cq")) != EOF) {
		switch (c) {
		case 'C':
			Cflag = 1;
	int c;

	while ((c = getopt(argc, argv, "snrg")) != EOF) {
		switch (c) {
		case 's':
			flags |= BDRV_O_SNAPSHOT;
	progname = basename(argv[0]);

	while ((c = getopt_long(argc, argv, sopt, lopt, &opt_index)) != -1) {
		switch (c) {
		case 's':
			flags |= BDRV_O_SNAPSHOT;