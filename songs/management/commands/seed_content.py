from django.core.management.base import BaseCommand
from songs.models import Song
from bible_study.models import BibleStudyNote
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed songs and bible study notes'

    def handle(self, *args, **options):
        self.stdout.write('Seeding songs and bible study notes...')

        songs_data = [
            {
                'title': 'Amazing Grace',
                'category': 'hymn',
                'lyrics': 'Amazing grace, how sweet the sound\nThat saved a wretch like me\nI once was lost, but now am found\nWas blind, but now I see\n\n\'Twas grace that taught my heart to fear\nAnd grace my fears relieved\nHow precious did that grace appear\nThe hour I first believed',
                'author': 'John Newton',
                'key': 'G',
                'tempo': 'Slow',
            },
            {
                'title': 'How Great Thou Art',
                'category': 'hymn',
                'lyrics': 'O Lord my God, when I in awesome wonder\nConsider all the worlds Thy hands have made\nI see the stars, I hear the rolling thunder\nThy power throughout the universe displayed\n\nThen sings my soul, my Savior God, to Thee\nHow great Thou art, how great Thou art',
                'author': 'Stuart K. Hine',
                'key': 'A',
                'tempo': 'Moderate',
            },
            {
                'title': 'Blessed Assurance',
                'category': 'hymn',
                'lyrics': 'Blessed assurance, Jesus is mine!\nO what a foretaste of glory divine!\nHeir of salvation, purchase of God\nBorn of His Spirit, washed in His blood\n\nThis is my story, this is my song\nPraising my Savior all the day long',
                'author': 'Fanny Crosby',
                'key': 'F',
                'tempo': 'Moderate',
            },
            {
                'title': 'Way Maker',
                'category': 'worship',
                'lyrics': 'Way maker, miracle worker\nPromise keeper, light in the darkness\nMy God, that is who You are\n\nYou are here, moving in our midst\nI worship You, I worship You\nYou are here, working in this place\nI worship You, I worship You',
                'author': 'Sinach',
                'key': 'E',
                'tempo': 'Moderate',
            },
            {
                'title': 'What a Beautiful Name',
                'category': 'worship',
                'lyrics': 'What a beautiful Name it is\nWhat a beautiful Name it is\nThe Name of Jesus Christ my King\nWhat a beautiful Name it is\nNothing compares to this\nWhat a beautiful Name it is\nThe Name of Jesus',
                'author': 'Hillsong',
                'key': 'D',
                'tempo': 'Moderate',
            },
            {
                'title': 'Great Are You Lord',
                'category': 'contemporary',
                'lyrics': 'Great are You Lord, it\'s Your breath in our lungs\nSo we pour out our praise, pour out our praise\nGreat are You Lord, it\'s Your breath in our lungs\nSo we pour out our praise to You only',
                'author': 'All Sons & Daughters',
                'key': 'G',
                'tempo': 'Moderate',
            },
            {
                'title': '10,000 Reasons',
                'category': 'contemporary',
                'lyrics': 'Bless the Lord, O my soul\nO my soul\nWorship His holy name\nSing like never before\nO my soul\nI\'ll worship Your holy name\n\nThe sun comes up, it\'s a new day dawning\nIt\'s time to sing Your song again',
                'author': 'Matt Redman',
                'key': 'E',
                'tempo': 'Moderate',
            },
            {
                'title': 'Lord I Lift Your Name on High',
                'category': 'praise',
                'lyrics': 'Lord I lift Your name on high\nI\'m so glad You\'re in my life\nI\'m glad You came to save us\n\nYou came from heaven to earth\nTo show the way\nFrom the earth to the cross\nMy debt to pay\nFrom the cross to the grave\nFrom the grave to the sky\nLord I lift Your name on high',
                'author': 'Rick Founds',
                'key': 'G',
                'tempo': 'Upbeat',
            },
        ]

        for song_data in songs_data:
            Song.objects.get_or_create(title=song_data['title'], defaults=song_data)

        self.stdout.write(self.style.SUCCESS(f'Created {len(songs_data)} songs'))

        bible_studies = [
            {
                'title': 'The Power of Faith',
                'bible_verse': 'Hebrews 11:1-6',
                'study_date': date.today() - timedelta(days=7),
                'teacher': 'Pastor James Mwangi',
                'content': 'Faith is the foundation of our Christian walk. Without faith, it is impossible to please God. When we have faith, we believe that God exists and that He rewards those who earnestly seek Him.\n\nIn this study, we explore the different dimensions of faith:\n1. Saving Faith - that which brings us to Christ\n2. Living Faith - that which sustains us daily\n3. Victorious Faith - that which overcomes the world\n\nThe heroes of faith in Hebrews 11 demonstrated that faith is not just belief, but action. They acted on what they believed, even when circumstances seemed impossible.',
                'key_points': 'Faith is substance and evidence\nFaith pleases God\nFaith requires action\nFaith overcomes impossible situations',
                'prayer_points': 'Lord, increase our faith\nHelp us to trust You in difficult times\nGive us faith like Abraham\nLet our faith be evident in our actions',
            },
            {
                'title': 'Walking in Love',
                'bible_verse': '1 Corinthians 13:1-13',
                'study_date': date.today() - timedelta(days=14),
                'teacher': 'Pastor James Mwangi',
                'content': 'Love is the greatest virtue a Christian can possess. Without love, all our spiritual gifts, knowledge, and sacrifice amount to nothing.\n\nThe characteristics of love as described in 1 Corinthians 13 are:\n- Patient and kind\n- Not jealous or boastful\n- Not arrogant or rude\n- Does not insist on its own way\n- Not irritable or resentful\n- Does not rejoice at wrongdoing\n- Bears all things, believes all things\n- Hopes all things, endures all things\n\nLove never fails. It is eternal, surpassing both prophecies and tongues.',
                'key_points': 'Love is the greatest virtue\nLove is patient and kind\nLove never fails\nWithout love, nothing profits',
                'prayer_points': 'Lord, teach us to love unconditionally\nRemove selfishness from our hearts\nHelp us to be patient and kind\nLet Your love flow through us',
            },
            {
                'title': 'The Armor of God',
                'bible_verse': 'Ephesians 6:10-18',
                'study_date': date.today() - timedelta(days=21),
                'teacher': 'Pastor James Mwangi',
                'content': 'As Christians, we are engaged in spiritual warfare. Our battle is not against flesh and blood, but against spiritual forces of evil.\n\nThe full armor of God includes:\n1. Belt of Truth - foundation of all\n2. Breastplate of Righteousness - protects the heart\n3. Shoes of the Gospel of Peace - stability\n4. Shield of Faith - extinguishes enemy attacks\n5. Helmet of Salvation - protects the mind\n6. Sword of the Spirit - the Word of God\n7. Prayer - the means of communication and warfare\n\nWe must put on the FULL armor to stand against the schemes of the devil.',
                'key_points': 'We have a spiritual enemy\nThe armor is for standing, not attacking\nEvery piece is essential\nPrayer activates the armor',
                'prayer_points': 'Lord, help us put on the full armor daily\nTeach us to use the Word of Spirit\nGive us victory over the enemy\nProtect our minds and hearts',
            },
        ]

        for study_data in bible_studies:
            BibleStudyNote.objects.get_or_create(
                title=study_data['title'],
                bible_verse=study_data['bible_verse'],
                defaults=study_data
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(bible_studies)} bible study notes'))
